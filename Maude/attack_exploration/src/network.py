# MAUDE_HCS: maude_hcs
#
# Software Markings (UNCLASS)
# PWNDD Software
#
# Copyright (C) 2025 RTX BBN Technologies Inc. All Rights Reserved
#
# Contract No: HR00112590083
# Contractor Name: RTX BBN Technologies Inc.
# Contractor Address: 10 Moulton Street, Cambridge, Massachusetts 02138
#
# The U.S. Government's rights to use, modify, reproduce, release, perform,
# display, or disclose these technical data and software are defined in the
# Article VII: Data Rights clause of the OTA.
#
# This document does not contain technology or technical data controlled under
# either the U.S. International Traffic in Arms Regulations or the U.S. Export
# Administration Regulations.
#
# DISTRIBUTION STATEMENT A: Approved for public release; distribution is
# unlimited.
#
# Notice: Markings. Any reproduction of this computer software, computer
# software documentation, or portions thereof must also reproduce the markings
# contained herein.
#
# MAUDE_HCS: end

import logging
logger = logging.getLogger(__name__)

class ParameterizedNetwork:
  '''
  The class for defining a network with parameterized links: i.e., the network
  can be defined as a set of links with different attributes.
  '''
  def __init__(self, nodes, links, link_characteristics_args) -> None:
    '''
    Constructor.
    nodes: The list of node names as they will appear in the rest of the config.
    links: The dictionary of link args as a link : linkType.
    link_characteristics_args:  The dictionary of link attributes
                                linkType : link obj.
    '''
    self.nodes  = nodes
    self.link_dict  = dict()
    for link_type in link_characteristics_args:
      link_characteristics = link_characteristics_args.get(link_type)
      self.link_dict[link_type] = ParameterizedLink(link_characteristics)

    self.links  = links
    self.parameters = link_characteristics_args


  def to_maude_network(self) -> str:
    '''
    Turn object to maude code.
    Return the string of the maude code to place in experiment file.
    '''
    maude_str   = " --- Link Characteristic definitions\n"
    for link_type, link in self.link_dict.items():
      maude_str  += f"op {link_type} : -> AttributeSet .\n"
      maude_str  += f"eq {link_type} = \n"
      maude_str  += link._to_maude()
      maude_str  += "\n  .\n\n"

    maude_str += f"eq LinkData =\n"
    maude_str += self._links_to_maude()
    return maude_str


  def _links_to_maude(self) -> str:
    '''
    Turn object links to maude code.
    Return the string of the maude code for the links.
    '''
    maude_str = ""
    for link, link_type in self.links.items():
      source_str  = ""
      dest_str    = ""
      if "<->" in link:
        source_str, dest_str = link.split("<->")
      elif "->" in link:
        source_str, dest_str  = link.split("->")
      elif "<-" in link:
        dest_str, source_str  = link.split("<-")
      # Get the proper node address (we have names that are just a partial 
      # match). nodes will looks something like: [addrNScorporate, addrNSpwnd2, 
      #                                           rAddr]
      # and the source and dest addresses are more like: pwnd2 or corporate.
      source_address  = list(map(lambda node: node.address, filter(
        lambda source_addr: source_str in source_addr.address, self.nodes)))[0]
      dest_address  = list(map(lambda node: node.address, filter(
        lambda dest_addr: dest_str in dest_addr.address, self.nodes)))[0]
      maude_str += f"  aaa({source_address},{dest_address},{link_type})\n"
    maude_str += "  .\n"
    return maude_str


class ParameterizedLink:
  '''
  The class for defining parameterized links.
  '''
  def __init__(self, parameters_args) -> None:
    '''
    Constructor.
    parameters_args:  The dict of arguments for a link (see below).
    '''
    self.delayType  = parameters_args.get("delayType", "constant")
    self.noiseMin   = parameters_args.get("noiseMin", 0.0)
    self.noiseMax   = parameters_args.get("noiseMax", 0.00001)
    self.delayConst = parameters_args.get("delayConst", 0.)
    self.delayMean  = parameters_args.get("delayMean", 0.)
    self.delayStd   = parameters_args.get("delayStd", 0.)
    self.canDrop    = parameters_args.get("canDrop", False)
    self.dropP      = parameters_args.get("dropP", 0.)

  def _to_maude(self) -> str:
    '''
    Turn object to maude code.
    Return the string of the maude code for this object.
    '''
    maude_str = ""
    terminator= ''
    for parameter, value in self.__dict__.items():
      if isinstance(value, str):
        maude_str += f'{terminator}  ({parameter}: "{str(value)}")'
      elif isinstance(value, bool):
        maude_str += f"{terminator}  ({parameter}: {str(value).lower()})"
      else:
        formatted_value = f"{value:f}"
        maude_str += f"{terminator}  ({parameter}: {formatted_value.rstrip('0')})"
      terminator = ',\n'
    return maude_str

