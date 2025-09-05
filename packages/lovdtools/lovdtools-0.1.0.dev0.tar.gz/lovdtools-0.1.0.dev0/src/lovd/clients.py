"""
LOVD Clients
============

Interfaces for querying the Leiden Open Variants Database (LOVD).

"""
from __future__ import annotations

import logging
import os
import time
from pathlib import Path
from typing import Any, TypeAlias

import polars as pl
import requests
import yaml
from dotenv import load_dotenv
from returns.result import Failure, Success
from tqdm import tqdm

from .constants import EMAIL, TARGETS, USER_AGENT

# : logger setup
logging.basicConfig(
    level="INFO",
    format="%(name)s – %(message)s"
)
logger = logging.getLogger(__name__)
logger.info("Logger setup complete.")


# : type aliases
PathLike: TypeAlias = os.PathLike


# : get enviornment variables from `.env`
load_dotenv()


# : rate limiting
LOVD_RATE_LIMIT = 5  # requests per second
LOVD_REQUEST_INTERVAL: float = 1.0 / LOVD_RATE_LIMIT


# : pathogenicity classifications
PATHOGENIC_CLASSIFICATIONS = {
    "pathogenic": ["pathogenic", "p", "disease-causing", "causal"],
    "likely_pathogenic": [
        "likely pathogenic", "lp", "probably pathogenic", "prob pathogenic"
    ],
    "vus": [
        "vus", "uncertain significance", "unknown significance", 
        "variant of uncertain significance", "vous", "uncertain"
    ],
    "likely_benign": ["likely benign", "lb", "probably benign", "prob benign"],
    "benign": ["benign", "b", "not pathogenic", "non-pathogenic", "polymorphism"]
}


def normalize_pathogenicity(value: str | None) -> str | None:
    """
    Normalize pathogenicity classification to standard terms.
    
    Parameters
    ----------
    value : str | None
        Raw pathogenicity value from LOVD
        
    Returns
    -------
    str | None
        Normalized pathogenicity classification or None if unclassifiable
    """
    if not value or not isinstance(value, str):
        return None
        
    value_lower = value.lower().strip()
    
    for classification, variants in PATHOGENIC_CLASSIFICATIONS.items():
        if any(variant in value_lower for variant in variants):
            return classification
            
    return None


# : interface
class LovdApiClient:
    """
    Client for interacting with the LOVD (Leiden Open Variation Database) API.

    Implements rate limiting to respect LOVD's 5 requests per second limit
    and sets appropriate user agent headers. Supports pathogenicity-based
    filtering and flexible search constraints.
    """

    def __init__(
        self,
        email: str | None = None,
        target_genes: list[str] | None = None,
        user_agent: str | None = None,
        logging_level: int = 1,
        show_progress: bool = False
    ) -> None:
        """
        Initialize the LOVD API client.

        Parameters
        ----------
        email : str, optional
            Email address for user agent identification. If not provided,
            will attempt to load from LOVD_EMAIL environment variable.
        target_genes : str, optional
            The list of gene symbols for which to search the database.
        user_agent : str, optional
            A short description of your application and its use cases.
        logging_level : int, default `1`
            An integer value that determines how verbose the client's
            logging output should be. If `0`, the client's acquisition
            routines will not emit any logs.
        show_progress : bool, default `False`
            A boolean value that determines whether to show the client's
            progress indicator. Requires the `tqdm` package.

        """
        # Bind parameters to `self`.
        self.email: str = email or EMAIL or os.getenv("LOVD_EMAIL", "")
        self.target_genes: list[str] = (
            target_genes
            or TARGETS
            or os.getenv("TARGETS", [])
        )
        self.user_agent: str = (
            user_agent or USER_AGENT or os.getenv("USER_AGENT")
        )

        self.ops_logging_level: int = logging_level
        if self.ops_logging_level > 0:
            logging.basicConfig(
                level=("CRITICAL" if logging_level == 1
                       else "ERROR" if logging_level == 2
                       else "WARNING" if logging_level == 3
                       else "INFO" if logging_level == 4
                       else "DEBUG" if logging_level == 5
                       else 1)
            )
            self.logger = logging.getLogger(__class__.__name__)
            self.logger.info("Logger setup complete.")

        self.ops_show_progress: bool = show_progress

        self.base_url: str = "https://databases.lovd.nl/shared/api/rest.php"
        self.last_request_time: float = 0.0

        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": self.user_agent,
            "Accept": "application/json",
        })


    # : dunder methods

    def __repr__(self) -> str:
        return (f"LovdApiClient(email={self.email!r},\n"
                f"              target_genes={self.target_genes},\n"
                f"              user_agent={self.user_agent!r}),\n"
                f"              logging_level={self.ops_logging_level},\n"
                f"              show_progress={self.ops_show_progress}")


    def _rate_limit(self) -> None:
        """5 req./s, as per LOVD guidelines."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < LOVD_REQUEST_INTERVAL:
            sleep_time = LOVD_REQUEST_INTERVAL - time_since_last
            time.sleep(sleep_time)

        self.last_request_time = time.time()


    def get_variants_for_gene(
        self, 
        target_gene: str,
        search_terms: list[str] | None = None,
        pathogenicity_filter: list[str] | None = None,
        exclude_missing_pathogenicity: bool = False,
        custom_filters: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """
        Get variant data for a single gene from LOVD.

        Parameters
        ----------
        target_gene : str
            The gene symbol about which to query.
        search_terms : list[str] | None, optional
            Search terms to include in the LOVD query. Will be joined
            with OR logic.
        pathogenicity_filter : list[str] | None, optional
            List of pathogenicity classifications to include. Options:
            "pathogenic", "likely_pathogenic", "vus", "likely_benign", 
            "benign". If None, all variants are returned.
        exclude_missing_pathogenicity : bool, default False
            If True, exclude variants with missing pathogenicity data.
        custom_filters : dict[str, str] | None, optional
            Additional query parameters to filter results.

        Returns
        -------
        dict[str, Any]
            JSON response from LOVD API containing variant data.

        Raises
        ------
        requests.RequestException
            If the API request fails.

        """
        self._rate_limit()

        url = f"{self.base_url}/variants/{target_gene}"
        params = {"format": "application/json"}

        # Add search terms if provided
        if search_terms:
            search_query = " OR ".join(f'"{term}"' for term in search_terms)
            params["search"] = search_query

        # Add custom filters
        if custom_filters:
            params.update(custom_filters)

        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            json_data = response.json()
            
            # Apply post-download filtering
            if pathogenicity_filter or exclude_missing_pathogenicity:
                json_data = self._filter_by_pathogenicity(
                    json_data, 
                    pathogenicity_filter,
                    exclude_missing_pathogenicity
                )
            
            return json_data
            
        except requests.RequestException as e:
            raise requests.RequestException(
                f"Failed to fetch data for {target_gene}: {e}"
            )


    def _filter_by_pathogenicity(
        self, 
        data: dict[str, Any], 
        pathogenicity_filter: list[str] | None,
        exclude_missing: bool
    ) -> dict[str, Any]:
        """
        Filter variant data by pathogenicity classification.
        
        Parameters
        ----------
        data : dict[str, Any]
            Raw variant data from LOVD
        pathogenicity_filter : list[str] | None
            Pathogenicity classifications to include
        exclude_missing : bool
            Whether to exclude variants with missing pathogenicity data
            
        Returns
        -------
        dict[str, Any]
            Filtered variant data
        """
        # Handle different data structures
        if isinstance(data, list):
            variants = data
        elif isinstance(data, dict):
            if "variants" in data:
                variants = data["variants"]
            elif "data" in data:
                variants = data["data"]
            else:
                # Assume the dict itself contains variant fields
                variants = [data]
        else:
            return data

        filtered_variants = []
        
        for variant in variants:
            if not isinstance(variant, dict):
                continue
                
            # Look for pathogenicity in common field names
            pathogenicity_value = None
            for field in ["pathogenicity", "classification", 
                         "clinical_classification", "significance", "effect"]:
                if field in variant:
                    pathogenicity_value = variant[field]
                    break
            
            # Normalize pathogenicity
            normalized_path = normalize_pathogenicity(pathogenicity_value)
            
            # Apply exclusion for missing pathogenicity
            if exclude_missing and normalized_path is None:
                continue
                
            # Apply pathogenicity filter
            if pathogenicity_filter and normalized_path not in pathogenicity_filter:
                continue
                
            filtered_variants.append(variant)
        
        # Reconstruct the data structure
        if isinstance(data, list):
            return filtered_variants
        elif isinstance(data, dict):
            filtered_data = data.copy()
            if "variants" in data:
                filtered_data["variants"] = filtered_variants
            elif "data" in data:
                filtered_data["data"] = filtered_variants
            else:
                filtered_data = filtered_variants[0] if filtered_variants else {}
            return filtered_data
        
        return data


    def get_variants_for_genes(
        self, 
        target_genes: list[str],
        save_to: PathLike | None = None,
        search_terms: list[str] | None = None,
        pathogenicity_filter: list[str] | None = None,
        exclude_missing_pathogenicity: bool = False,
        custom_filters: dict[str, str] | None = None,
        show_progress: bool = False
    ) -> dict[str, dict[str, Any]]:
        """
        Get variant data for multiple genes from LOVD.

        Parameters
        ----------
        target_genes : list[str]
            List of gene symbols to query.
        save_to : PathLike | None, optional
            Directory path to save the JSON data. If provided, will save
            individual JSON files for each gene.
        search_terms : list[str] | None, optional
            Search terms to include in the LOVD query.
        pathogenicity_filter : list[str] | None, optional
            List of pathogenicity classifications to include. Options:
            "pathogenic", "likely_pathogenic", "vus", "likely_benign", 
            "benign". If None, all variants are returned.
        exclude_missing_pathogenicity : bool, default False
            If True, exclude variants with missing pathogenicity data.
        custom_filters : dict[str, str] | None, optional
            Additional query parameters to filter results.
        show_progress : bool, default False
            Whether to show progress bar during download.

        Returns
        -------
        dict[str, dict[str, Any]]
            A dictionary that maps gene symbols to their variants.

        """
        if self.ops_logging_level > 0:
            self.logger.level = (logging.CRITICAL if self.ops_logging_level == 1
                                else logging.ERROR if self.ops_logging_level == 2
                                else logging.WARNING if self.ops_logging_level == 3
                                else logging.INFO if self.ops_logging_level == 4
                                else logging.DEBUG if self.ops_logging_level == 5
                                else 1)
        
        downloaded = {}
        target_genes = (tqdm(target_genes) if (show_progress or self.ops_show_progress) 
                       else target_genes)

        for gene_symbol in target_genes:
            try:
                if self.ops_logging_level > 0:
                    filter_desc = []
                    if search_terms:
                        filter_desc.append(f"search: {search_terms}")
                    if pathogenicity_filter:
                        filter_desc.append(f"pathogenicity: {pathogenicity_filter}")
                    
                    filter_msg = (f" ({', '.join(filter_desc)})" 
                                 if filter_desc else "")
                    self.logger.info(f"Fetching variants for {gene_symbol}{filter_msg}...")

                data = self.get_variants_for_gene(
                    gene_symbol,
                    search_terms=search_terms,
                    pathogenicity_filter=pathogenicity_filter,
                    exclude_missing_pathogenicity=exclude_missing_pathogenicity,
                    custom_filters=custom_filters
                )

                downloaded[gene_symbol] = data

                if save_to:
                    save_path = Path(save_to)
                    save_path.mkdir(parents=True, exist_ok=True)

                    # Create descriptive filename
                    suffix_parts = []
                    if search_terms:
                        suffix_parts.append("filtered")
                    if pathogenicity_filter:
                        suffix_parts.append("pathogenic")
                    
                    suffix = f"_{'_'.join(suffix_parts)}_variants.json" if suffix_parts else "_variants.json"
                    gene_file = save_path / f"{gene_symbol}{suffix}"

                    with open(gene_file, "w", encoding="utf-8") as f:
                        # Save as JSON instead of YAML for better performance
                        import json
                        json.dump({gene_symbol: data}, f, indent=2, ensure_ascii=False)

                    if self.ops_logging_level > 0:
                        self.logger.info(f"Saved {gene_symbol} data to `{gene_file}`.")

            except requests.RequestException as e:
                if self.ops_logging_level > 1:
                    self.logger.error(f"Error fetching data for {gene_symbol}: {e}")

                downloaded[gene_symbol] = {"error": str(e)}

        # Save combined data if save_to is provided
        if save_to:
            save_path = Path(save_to)
            suffix_parts = []
            if search_terms:
                suffix_parts.append("filtered")
            if pathogenicity_filter:
                suffix_parts.append("pathogenic")
            
            suffix = f"_{'_'.join(suffix_parts)}_variants.json" if suffix_parts else "_variants.json"
            combined_file = save_path / f"all{suffix}"
            
            with open(combined_file, "w", encoding="utf-8") as f:
                import json
                json.dump(downloaded, f, indent=2, ensure_ascii=False)

            if self.ops_logging_level >= 4:
                self.logger.info(f"Saved combined data to `{combined_file}`.")

        return downloaded


    # : chainable methods

    def with_progress_indication(self) -> LovdApiClient:
        """Enable the client's `tqdm` progress indicator."""
        self.ops_show_progress = True
        return self


    def with_logging(self, level=1) -> LovdApiClient:
        """Enable the client's logger."""
        self.ops_logging_level = level

        if not hasattr(self, "logger"):
            self.logger = logging.getLogger(__class__.__name__)
            self.logger.level = (logging.CRITICAL if self.ops_logging_level == 1
                                else logging.ERROR if self.ops_logging_level == 2
                                else logging.WARNING if self.ops_logging_level == 3
                                else logging.INFO if self.ops_logging_level == 4
                                else logging.DEBUG if self.ops_logging_level == 5
                                else 1)
            self.logger.info("`LovdApiClient` logger setup complete.")

        return self


def get_lovd_variants(
    genes: str | list[str],
    save_to: PathLike | None = None,
    search_terms: list[str] | None = None,
    pathogenicity_filter: list[str] | None = None,
    exclude_missing_pathogenicity: bool = False,
    custom_filters: dict[str, str] | None = None
) -> dict[str, dict[str, Any]]:
    """
    Get a JSON dictionary containing variants for the specified gene(s).

    Optionally, you can save the JSON to disk by passing a path-like
    object to `save_to`, which defaults to `None`.

    Parameters
    ----------
    genes : str | list[str]
        The symbol or symbols of the gene or genes whose variant data
        you are requesting.
    save_to : PathLike, optional
        A path-like object representing the path of the directory to
        which the downloaded data should be saved.
    search_terms : list[str] | None, optional
        Search terms to filter variants (e.g., disease names, phenotypes).
        Terms will be joined with OR logic.
    pathogenicity_filter : list[str] | None, optional
        List of pathogenicity classifications to include. Options:
        "pathogenic", "likely_pathogenic", "vus", "likely_benign", 
        "benign". If None, all variants are returned.
    exclude_missing_pathogenicity : bool, default False
        If True, exclude variants with missing pathogenicity data.
    custom_filters : dict[str, str] | None, optional
        Additional query parameters to filter results.

    Returns
    -------
    dict[str, dict]
        The data downloaded from LOVD, keyed by gene symbol.
    
    Examples
    --------
    >>> # Single gene, all variants
    >>> variants = get_lovd_variants("COL1A1")
    >>> 
    >>> # Multiple genes, pathogenic variants only
    >>> variants = get_lovd_variants(
    ...     ["COL1A1", "COL3A1"], 
    ...     pathogenicity_filter=["pathogenic", "likely_pathogenic"]
    ... )
    >>> 
    >>> # Search for specific disease
    >>> variants = get_lovd_variants(
    ...     ["COL1A1"], 
    ...     search_terms=["Ehlers-Danlos", "connective tissue disorder"]
    ... )
    >>> 
    >>> # Exclude variants without pathogenicity data
    >>> variants = get_lovd_variants(
    ...     ["COL1A1"], 
    ...     exclude_missing_pathogenicity=True
    ... )
    >>> 
    >>> # Save to disk
    >>> variants = get_lovd_variants(
    ...     ["COL1A1", "COL3A1"], 
    ...     save_to="./lovd_data"
    ... )
    """
    if isinstance(genes, str):
        genes = [genes]

    client = LovdApiClient()

    return client.get_variants_for_genes(
        genes,
        save_to=save_to, 
        search_terms=search_terms,
        pathogenicity_filter=pathogenicity_filter,
        exclude_missing_pathogenicity=exclude_missing_pathogenicity,
        custom_filters=custom_filters
    )


def get_pathogenic_variants_only(
    genes: str | list[str],
    save_to: PathLike | None = None,
    search_terms: list[str] | None = None,
    include_likely_pathogenic: bool = True,
    exclude_missing_pathogenicity: bool = True
) -> dict[str, dict[str, Any]]:
    """
    Convenience function to get only pathogenic variants from LOVD.
    
    Parameters
    ----------
    genes : str | list[str]
        The symbol or symbols of the gene or genes whose variant data
        you are requesting.
    save_to : PathLike, optional
        A path-like object representing the path of the directory to
        which the downloaded data should be saved.
    search_terms : list[str] | None, optional
        Search terms to filter variants (e.g., disease names, phenotypes).
    include_likely_pathogenic : bool, default True
        Whether to include "likely pathogenic" variants along with
        "pathogenic" ones.
    exclude_missing_pathogenicity : bool, default True
        If True, exclude variants with missing pathogenicity data.
        
    Returns
    -------
    dict[str, dict]
        The pathogenic variant data downloaded from LOVD.
        
    Examples
    --------
    >>> # Get pathogenic variants for EDS genes
    >>> pathogenic_variants = get_pathogenic_variants_only(
    ...     ["COL1A1", "COL3A1", "COL5A1"],
    ...     search_terms=["Ehlers-Danlos"]
    ... )
    >>> 
    >>> # Get only definitively pathogenic variants (exclude likely pathogenic)
    >>> strict_pathogenic = get_pathogenic_variants_only(
    ...     ["BRCA1", "BRCA2"],
    ...     include_likely_pathogenic=False
    ... )
    """
    pathogenicity_filter = ["pathogenic"]
    if include_likely_pathogenic:
        pathogenicity_filter.append("likely_pathogenic")
    
    return get_lovd_variants(
        genes,
        save_to=save_to,
        search_terms=search_terms,
        pathogenicity_filter=pathogenicity_filter,
        exclude_missing_pathogenicity=exclude_missing_pathogenicity
    )


def filter_variants_by_pathogenicity(
    variants_data: dict[str, dict[str, Any]],
    pathogenicity_filter: list[str],
    exclude_missing: bool = False,
    show_progress: bool = False
) -> dict[str, dict[str, Any]]:
    """
    Post-process downloaded variant data to filter by pathogenicity.
    
    This function is useful for filtering variants after download when
    you want to apply different pathogenicity criteria to the same dataset.
    
    Parameters
    ----------
    variants_data : dict[str, dict]
        Raw variant data downloaded from LOVD.
    pathogenicity_filter : list[str]
        List of pathogenicity classifications to include. Options:
        "pathogenic", "likely_pathogenic", "vus", "likely_benign", "benign".
    exclude_missing : bool, default False
        If True, exclude variants with missing pathogenicity data.
    show_progress : bool, default False
        Whether to display a progress indicator during filtering.
        
    Returns
    -------
    dict[str, dict]
        Filtered variant data containing only specified pathogenicity classes.
    """
    filtered_data = {}
    items = tqdm(variants_data.items()) if show_progress else variants_data.items()

    for gene_symbol, gene_data in items:
        if "error" in gene_data:
            filtered_data[gene_symbol] = gene_data
            continue
            
        # Use the same filtering logic as the client
        client = LovdApiClient()
        filtered_gene_data = client._filter_by_pathogenicity(
            gene_data, pathogenicity_filter, exclude_missing
        )
        
        # Only include genes with remaining variants
        if filtered_gene_data:
            filtered_data[gene_symbol] = filtered_gene_data
    
    return filtered_data


def variants_to_dataframe(
    variants_data: dict[str, dict[str, Any]],
    normalize_pathogenicity: bool = True,
    show_progress: bool = False
) -> pl.DataFrame:
    """
    Convert LOVD variants data to a Polars DataFrame for analysis.
    
    Parameters
    ----------
    variants_data : dict[str, dict]
        Dictionary of variant data returned by get_lovd_variants.
    normalize_pathogenicity : bool, default True
        Whether to add a normalized pathogenicity column using standard
        classifications.
    show_progress : bool, default False
        Whether to display a progress indicator during conversion.
        
    Returns
    -------
    polars.DataFrame
        DataFrame containing flattened variant data with gene symbol added.

    """
    all_variants = []
    items = tqdm(variants_data.items()) if show_progress else variants_data.items()

    for gene_symbol, gene_data in items:
        if "error" in gene_data:
            continue

        # Handle different data structures
        if isinstance(gene_data, list):
            variants = gene_data
        elif isinstance(gene_data, dict):
            variants = gene_data.get("variants", gene_data.get("data", [gene_data]))
        else:
            continue

        for variant in variants:
            if not isinstance(variant, dict):
                continue
                
            variant_copy = variant.copy()
            variant_copy["gene_symbol"] = gene_symbol
            
            # Add normalized pathogenicity if requested
            if normalize_pathogenicity:
                # Look for pathogenicity in common field names
                pathogenicity_value = None
                for field in ["pathogenicity", "classification", 
                             "clinical_classification", "significance", "effect"]:
                    if field in variant:
                        pathogenicity_value = variant[field]
                        break
                
                variant_copy["pathogenicity_normalized"] = normalize_pathogenicity(
                    pathogenicity_value
                )
                
            all_variants.append(variant_copy)
 
    return (pl.DataFrame(all_variants)
            if all_variants
            else pl.DataFrame({"gene_symbol": []}))
