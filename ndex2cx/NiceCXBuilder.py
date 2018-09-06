__author__ = 'aarongary'

import json
import ijson
import requests
import base64
import sys
#from urllib import urlopen
from ndex2.client import Ndex2
from ndex2.NiceCXNetwork import NiceCXNetwork
#from nicecxModel.cx.aspects.NodeElement import NodeElement
#from nicecxModel.cx.aspects.EdgeElement import EdgeElement
#from nicecxModel.cx.aspects.NetworkAttributesElement import NetworkAttributesElement
#from nicecxModel.cx.aspects.NodeAttributesElement import NodeAttributesElement
#from nicecxModel.cx.aspects.EdgeAttributesElement import EdgeAttributesElement
#from nicecxModel.cx.aspects.CitationElement import CitationElement
#from nicecxModel.cx.aspects.SupportElement import SupportElement
#from nicecxModel.cx.aspects.AspectElement import AspectElement
#from nicecxModel.metadata.MetaDataElement import MetaDataElement
#from nicecxModel.cx.aspects import ATTRIBUTE_DATA_TYPE
#from nicecxModel.cx.aspects.SimpleNode import SimpleNode
#from nicecxModel.cx import CX_CONSTANTS
#from nicecxModel.cx import known_aspects, known_aspects_min

if sys.version_info.major == 3:
    from urllib.request import urlopen, Request, HTTPBasicAuthHandler, HTTPPasswordMgrWithDefaultRealm, \
        build_opener, install_opener, HTTPError, URLError
else:
    from urllib2 import urlopen, Request, HTTPBasicAuthHandler, HTTPPasswordMgrWithDefaultRealm, \
        build_opener, install_opener, HTTPError, URLError

class NiceCXBuilder(object):
    def __init__(self, cx=None, server=None, username='scratch', password='scratch', uuid=None, networkx_G=None, data=None, **attr):
        self.nice_cx = NiceCXNetwork(user_agent='niceCx Builder')
        self.node_id_lookup = {}
        self.node_id_counter = 0
        self.edge_id_counter = 0

        self.node_inventory = {}
        self.node_attribute_inventory = []

        self.edge_inventory = {}
        self.edge_attribute_inventory = []

        self.opaque_aspect_inventory = []

        self.context_inventory = []

        self.network_attribute_inventory = {}

        self.user_base64 = None
        self.username = None
        self.password = None
        if username and password:
            self.username = username
            self.password = password
            if sys.version_info.major == 3:
                encode_string = '%s:%s' % (username, password)
                byte_string = encode_string.encode()
                self.user_base64 = base64.b64encode(byte_string)#.replace('\n', '')
            else:
                self.user_base64 = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')

    def set_context(self, context):
        """
        Set the @context information of the network.  This information maps namespace prefixes to their defining URIs

        Example:

            ``set_context({'pmid': 'https://www.ncbi.nlm.nih.gov/pubmed/'})``

        :param context: dict of name, URI pairs
        :type context: dict
        :return: None
        :rtype: none
        """
        if isinstance(context, dict):
            self.context_inventory = context
        elif isinstance(context, list):
            if len(context) > 0:
                self.context_inventory = context[0]

    def set_name(self, network_name):
        """
        Set the network name

        :param network_name: Network name
        :type network_name: string
        :return: None
        :rtype:none
        """

        self.network_attribute_inventory['name'] = {'n': 'name', 'v': network_name, 'd': 'string'}

    def add_network_attribute(self, name=None, values=None, type=None, cx_element=None):
        """
        Add an attribute to the network

        :param name: Name of the attribute
        :type name: str
        :param values:  The value(s) of the attribute
        :type values: One of the allowable CX types.  See `Supported data types`_
        :param type: They type of data supplied in values. Default is string.  See `Supported data types`_
        :type type: str
        :return: None
        :rtype: None
        """

        add_this_network_attribute = {'n': name, 'v': values}
        if type:
            add_this_network_attribute['d'] = type

        self.network_attribute_inventory[name] = add_this_network_attribute

    def add_node(self, name=None, represents=None, id=None, data_type=None):
        """
        Adds a new node with the corresponding name and represents (external id)

        :param node_name: Name of the node
        :type node_name: str
        :param represents: Representation of the node (alternate identifier)
        :type represents: str
        :param id:
        :type id:
        :return: Node ID
        :rtype: int
        """
        if self.node_inventory.get(name) is not None:
            return self.node_inventory.get(name).get('@id')

        if id:
            node_id = id
        else:
            node_id = self.node_id_counter
            self.node_id_counter += 1

        add_this_node = {'@id': node_id, 'n': name}
        if represents:
            add_this_node['r'] = represents
        if data_type:
            add_this_node['d'] = data_type

        self.node_inventory[name] = add_this_node

        return node_id

    def add_edge(self, source=None, target=None, interaction=None, id=None):
        """
        Adds a new edge in the network by specifying source-interaction-target

        :param source: The source node of this edge, either its id or the node object itself.
        :type source: int, dict (with @id property)
        :param target: The target node of this edge, either its id or the node object itself.
        :type target: int, dict (with @id property)
        :param interaction: The interaction that describes the relationship between the source and target nodes
        :type interaction: str
        :param id: Edge id for this edge.  If none is provided the builder will create one
        :type id: int
        :return: Edge ID
        :rtype: int
        """

        if id is not None:
            edge_id = id
        else:
            edge_id = self.edge_id_counter
            self.edge_id_counter += 1

        add_this_edge = {'@id': edge_id, 's': source, 't': target}
        if interaction:
            add_this_edge['i'] = interaction
        else:
            add_this_edge['i'] = 'interacts-with'

        self.edge_inventory[edge_id] = add_this_edge

        return edge_id

    def add_node_attribute(self, property_of, name, value, type=None):
        """
        Set an attribute of a node, where the node may be specified by its id or passed in as a node dict.

        :param property_of: Node ID to add the attribute to
        :type property_of: int
        :param name: Attribute name
        :type name: str
        :param value: A value or list of values of the attribute
        :type value: list, string, int or float
        :param type: The datatype of the attribute values, defaults is string.  See `Supported data types`_
        :type type: str
        :return: None
        :rtype: None
        """
        add_this_node_attribute = {'po': property_of, 'n': name, 'v': value}
        if type:
            add_this_node_attribute['d'] = type
        self.node_attribute_inventory.append(add_this_node_attribute)

    def add_edge_attribute(self, property_of=None, name=None, values=None, type=None):
        """
        Set the value(s) of attribute of an edge, where the edge may be specified by its id or passed in an object.

        Example:

            ``set_edge_attribute(0, 'weight', 0.5, type='float')``

            or

            ``set_edge_attribute(edge, 'Disease', 'Atherosclerosis')``

        :param property_of: Edge to add the attribute to
        :type property_of: int or edge dict with @id attribute
        :param name: Attribute name
        :type name: str
        :param values: A value or list of values of the attribute
        :type values: list, string, int or float
        :param type: The datatype of the attribute values, defaults to the python datatype of the values.  See `Supported data types`_
        :type type: str
        :return: None
        :rtype: None
        """
        add_this_edge_attribute = {'po': property_of, 'n': name, 'v': values}
        if type:
            add_this_edge_attribute['d'] = type
        self.edge_attribute_inventory.append(add_this_edge_attribute)

    def add_opaque_aspect(self, oa_name, oa_list):
        self.opaque_aspect_inventory.append({oa_name: oa_list})

    #===================================
    # methods to add data by fragment
    #===================================
    def _add_network_attributes_from_fragment(self, fragment):
        self.nice_cx.networkAttributes.append(fragment)

    def _add_node_from_fragment(self, fragment):
        self.nice_cx.nodes[fragment.get('@id')] = fragment

    def _add_edge_from_fragment(self, fragment):
        self.nice_cx.edges[fragment.get('@id')] = fragment

    def _add_node_attribute_from_fragment(self, fragment):
        if self.nice_cx.nodeAttributes.get(fragment.get('po')) is None:
            self.nice_cx.nodeAttributes[fragment.get('po')] = []

        self.nice_cx.nodeAttributes[fragment.get('po')].append(fragment)

    def _add_edge_attribute_from_fragment(self, fragment):
        if self.nice_cx.edgeAttributes.get(fragment.get('po')) is None:
            self.nice_cx.edgeAttributes[fragment.get('po')] = []

        self.nice_cx.edgeAttributes[fragment.get('po')].append(fragment)

    def _add_citation_from_fragment(self, fragment):
        self.nice_cx.citations[fragment.get('@id')] = fragment

    def _add_supports_from_fragment(self, fragment):
        self.nice_cx.supports[fragment.get('@id')] = fragment

    def _add_edge_supports_from_fragment(self, fragment):
        for po_id in fragment.get('po'):
            self.nice_cx.edgeSupports[po_id] = fragment.get('supports')

    def _add_node_citations_from_fragment(self, fragment):
        for po_id in fragment.get('po'):
            self.nice_cx.nodeCitations[po_id] = fragment.get('citations')

    def _add_edge_citations_from_fragment(self, fragment):
        for po_id in fragment.get('po'):
            self.nice_cx.edgeCitations[po_id] = fragment.get('citations')

    def get_nice_cx(self):
        #==========================
        # ADD CONTEXT
        #==========================
        if isinstance(self.context_inventory, dict):
            self.nice_cx.set_context(self.context_inventory)
        else:
            for c in self.context_inventory:
                self.nice_cx.set_context(c)

        #=============================
        # ASSEMBLE NETWORK ATTRIBUTES
        #=============================
        #{'n': 'name', 'v': network_name, 'd': 'string'}
        for k, v in self.network_attribute_inventory.items():
            self.nice_cx.add_network_attribute(name=v.get('n'), values=v.get('v'), type=v.get('d'))

        #==========================
        # ASSEMBLE NODES
        #==========================
        for k, v in self.node_inventory.items():
            self.nice_cx.nodes[v.get('@id')] = v

        #==========================
        # ASSEMBLE NODE ATTRIBUTES
        #==========================
        for a in self.node_attribute_inventory:
            property_of = a.get('po')

            if self.nice_cx.nodeAttributes.get(property_of) is None:
                self.nice_cx.nodeAttributes[property_of] = []

            self.nice_cx.nodeAttributes[property_of].append(a)

        #==========================
        # ASSEMBLE EDGES
        #==========================
        for k, v in self.edge_inventory.items():
            self.nice_cx.edges[k] = v

        #==========================
        # ASSEMBLE EDGE ATTRIBUTES
        #==========================
        for a in self.edge_attribute_inventory:
            property_of = a.get('po')

            if self.nice_cx.edgeAttributes.get(property_of) is None:
                self.nice_cx.edgeAttributes[property_of] = []

            self.nice_cx.edgeAttributes[property_of].append(a)

        #==========================
        # ASSEMBLE OPAQUE ASPECTS
        #==========================
        for oa in self.opaque_aspect_inventory:
            for k, v in oa.items():
                self.nice_cx.add_opaque_aspect(k, v)

        return self.nice_cx

    def get_frag_from_list_by_key(self, cx, key):
        for aspect in cx:
            if key in aspect:
                return aspect[key]

        return []

    def load_aspect(self, aspect_name):
        #with open('Signal1.cx', mode='r') as cx_f:
        with open('network1.cx', mode='r') as cx_f:
            aspect_json = json.loads(cx_f.read())
            for aspect in aspect_json:
                if aspect.get(aspect_name) is not None:
                    return aspect.get(aspect_name)

    def stream_all_aspects(self, uuid):
        return ijson.items(urlopen('http://dev2.ndexbio.org/v2/network/' + uuid), 'item')

    def stream_aspect(self, uuid, aspect_name):
        if aspect_name == 'metaData':
            print('http://dev2.ndexbio.org/v2/network/' + uuid + '/aspect')
            md_response = requests.get('http://dev2.ndexbio.org/v2/network/' + uuid + '/aspect')
            json_respone = md_response.json()
            return json_respone.get('metaData')
        else:
            #password_mgr = HTTPPasswordMgrWithDefaultRealm()

            #top_level_url = 'http://dev2.ndexbio.org'
            #password_mgr.add_password(None, top_level_url, self.username, self.password)
            #handler = HTTPBasicAuthHandler(password_mgr)
            #opener = build_opener(handler)
            #install_opener(opener)





            # Create an OpenerDirector with support for Basic HTTP Authentication...
            #auth_handler = HTTPBasicAuthHandler()
            #auth_handler.add_password(None, 'http://dev2.ndexbio.org', 'scratch', 'scratch')
            #opener = build_opener(auth_handler)
            # ...and install it globally so it can be used with urlopen.
            #install_opener(opener)


            request = Request('http://dev2.ndexbio.org/v2/network/' + uuid + '/aspect/' + aspect_name)
            base64string = base64.b64encode('%s:%s' % ('scratch', 'scratch'))
            request.add_header("Authorization", "Basic %s" % base64string)
            #result = urllib2.urlopen(request)


            urlopen_result = None
            try:
                urlopen_result = urlopen(request) #'http://dev2.ndexbio.org/v2/network/' + uuid + '/aspect/' + aspect_name)
            except HTTPError as e:
                print(e.code)
                return []
            except URLError as e:
                print('Other error')
                print('URL Error %s' % e.message())
                return []

            return ijson.items(urlopen_result, 'item')

    def stream_aspect_raw(self, uuid, aspect_name):
        return ijson.parse(urlopen('http://dev2.ndexbio.org/v2/network/' + uuid + '/aspect/' + aspect_name))


