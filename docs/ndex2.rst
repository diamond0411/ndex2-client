NiceCXNetwork module
--------------------------
The NiceCXNetwork class provides a data model for working with NDEx networks.  Methods are provided to add nodes, edges, node attributes, edge attributes, etc.  Once a NiceCXNetwork data object is populated it can be saved to the NDEx server by calling either **upload_to()** to create a new network or **update_to()** to update an existing network.


To see deprecated methods go to `Deprecated NiceCXNetwork methods`_


Methods for building niceCX
===========================
see also
`this notebook <https://github.com/ndexbio/ndex-jupyter-notebooks/blob/master/notebooks/NiceCX%20v2.0%20Tutorial.ipynb>`_

Node methods
****************************
.. autoclass:: ndex2.NiceCXNetwork.NiceCXNetwork
    :members: create_node, set_node_attribute

Edge methods
****************************
.. autoclass:: ndex2.NiceCXNetwork.NiceCXNetwork
    :members: create_edge, set_edge_attribute

Network methods
****************************
.. autoclass:: ndex2.NiceCXNetwork.NiceCXNetwork
    :members: set_context, set_name, set_network_attribute, set_opaque_aspect

Methods for accessing niceCX properties
========================================
see also
`this notebook <https://github.com/ndexbio/ndex-jupyter-notebooks/blob/master/notebooks/NiceCX%20v2.0%20navigating%20the%20network.ipynb>`_

Node methods
****************************
.. autoclass:: ndex2.NiceCXNetwork.NiceCXNetwork
    :members: get_node_attribute, get_node_attribute_value, get_node_attributes, get_nodes

Edge methods
****************************
.. autoclass:: ndex2.NiceCXNetwork.NiceCXNetwork
    :members: get_edge_attribute, get_edge_attribute_value, get_edge_attributes, get_edges

Network methods
****************************
.. autoclass:: ndex2.NiceCXNetwork.NiceCXNetwork
    :members: get_context, get_name, get_network_attribute, get_network_attributes, get_opaque_aspect

Misc niceCX methods
========================================
.. autoclass:: ndex2.NiceCXNetwork.NiceCXNetwork
    :members: apply_template, print_summary, to_cx, to_cx_stream, to_networkx, to_pandas_dataframe, update_to, upload_to

Deprecated NiceCXNetwork methods
===========================
.. autoclass:: ndex2.NiceCXNetwork.NiceCXNetwork
    :members: add_edge, add_node, get_edge_attribute_objects, get_node_attribute_objects, get_summary, set_provenance, get_provenance

Supported data types
=====================
The following data types are supported in methods that accept **type**

    Example:

        ``set_edge_attribute(0, 'weight', 0.5, type='double')``


* string
* double
* boolean
* integer
* long
* list_of_string
* list_of_double
* list_of_boolean
* list_of_integer
* list_of_long


Methods for creating niceCX from other data models
=============
.. automodule:: ndex2
    :members: create_nice_cx_from_raw_cx, create_nice_cx_from_file, create_nice_cx_from_networkx, create_nice_cx_from_pandas, create_nice_cx_from_server

Client access to NDEx server API
===========================

.. autoclass:: ndex2.client.Ndex2
    :members: add_networks_to_networkset, create_networkset, delete_network, delete_networks_from_networkset, get_neighborhood, get_neighborhood_as_cx_stream, get_network_as_cx_stream, get_network_ids_for_user, get_network_set, get_network_summary, get_sample_network, get_task_by_id, get_user_by_username, get_user_network_summaries, grant_network_to_user_by_username, grant_networks_to_group, grant_networks_to_user, make_network_private, make_network_public, save_cx_stream_as_new_network, save_new_network, search_networks, set_network_properties, set_network_system_properties, set_read_only, update_cx_network, update_network_group_permission, update_network_profile, update_network_user_permission

