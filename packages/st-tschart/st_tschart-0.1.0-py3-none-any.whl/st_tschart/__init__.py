"""
st-tschart: Streamlit Timeseries Chart Component

A Streamlit component for rendering interactive timeseries charts with CDF integration.
"""

import os
import hashlib
import json
from typing import Optional, Dict, Any, List, Union
import streamlit.components.v1 as components
from cognite.client import CogniteClient

# Create a _component_func which will call the frontend component.
_component_func = components.declare_component(
    "st_tschart",
    path=os.path.join(os.path.dirname(__file__), "frontend", "build"),
)


def timeseries_chart(
    items: List[Union[int, str]],
    cognite_client: CogniteClient,
    merge_units: bool = False,
    show_min_max: bool = False,
    height: int = 600,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    max_data_points: int = 1000,
    key: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Render an interactive timeseries chart with CDF integration.

    Parameters
    ----------
    items : list
        List of timeseries IDs (integers or strings) to display
    cognite_client : CogniteClient
        An authenticated CogniteClient instance for data access
    merge_units : bool, default False
        Whether to merge timeseries with the same units on the same y-axis
    show_min_max : bool, default False
        Whether to show min/max bands for aggregated data
    height : int, default 600
        Height of the chart in pixels
    start_date : str, optional
        Start date for the time range (ISO format). If not provided, defaults to 1 month ago
    end_date : str, optional
        End date for the time range (ISO format). If not provided, defaults to now
    max_data_points : int, default 1000
        Maximum number of data points to fetch per timeseries
    key : str, optional
        Unique component key. If not provided, a key will be automatically generated
        based on a hash of the parameters to ensure re-rendering when data changes.

    Returns
    -------
    dict
        Dictionary with the selected time range:
        - 'start': Start date of the selected time range (ISO format)
        - 'end': End date of the selected time range (ISO format)

    Examples
    --------
    >>> import streamlit as st
    >>> from st_tschart import timeseries_chart
    >>> from cognite.client import CogniteClient, ClientConfig
    >>> from cognite.client.credentials import Token
    >>>
    >>> # Create authenticated client
    >>> client = CogniteClient(
    ...     ClientConfig(
    ...         client_name="my-app",
    ...         project="your-project",
    ...         credentials=Token("your-token"),
    ...         base_url="https://api.cognitedata.com"
    ...     )
    ... )
    >>>
    >>> # Render timeseries chart
    >>> result = timeseries_chart(
    ...     items=[1222, 2323, 3333],
    ...     cognite_client=client,
    ...     merge_units=True,
    ...     show_min_max=True,
    ...     height=600
    ... )
    >>>
    >>> if result:
    ...     st.write("Selected time range:", result)
    """

    # Extract credentials from CogniteClient
    cdf_project = cognite_client.config.project
    cdf_base_url = cognite_client.config.base_url
    
    # Extract authorization header (the tuple contains ('Authorization', 'Bearer token'))
    auth_header = cognite_client.config.credentials.authorization_header()
    cdf_token = auth_header[1].replace('Bearer ', '') if auth_header and len(auth_header) > 1 else None
    
    if not cdf_token:
        raise ValueError("Unable to extract authentication token from CogniteClient")

    # Generate a unique key based on parameters if no key is provided
    if key is None:
        try:
            # Create a hash of the parameters
            params = {
                'items': items,
                'merge_units': merge_units,
                'show_min_max': show_min_max,
                'start_date': start_date,
                'end_date': end_date,
                'project': cdf_project,  # Include project in hash for uniqueness
            }
            params_str = json.dumps(params, sort_keys=True)
            params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]
            key = f"tschart_{params_hash}"
        except (TypeError, ValueError):
            # Fallback to a simple key if hashing fails
            key = "tschart_default"

    component_value = _component_func(
        items=items,
        merge_units=merge_units,
        show_min_max=show_min_max,
        cdf_token=cdf_token,
        cdf_project=cdf_project,
        cdf_base_url=cdf_base_url,
        height=height,
        start_date=start_date,
        end_date=end_date,
        max_data_points=max_data_points,
        key=key,
        default={'start': start_date, 'end': end_date},
    )

    return component_value


# Make timeseries_chart available at package level
__all__ = ["timeseries_chart"]