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
  It will try to create a new link profile for a set of parameters that are new,
  otherwise, it will link to that existing link profile.

  How to use:
  Initialize with edge information.
  Call create links with link definitions (source->dest).
  Call to write to maude language.

  Currently this class only supports unidirectionality. TODO: Support <->.
  Finally, call to_maude_network.
  '''
  def __init__(self, edge_info) -> None:
    '''
    Constructor.
    nodes: The list of nodes (resolvers, clients, etc.).
    edge_info: The DiGraph edges with data.
    '''
    # Edge characteristics: includes latency, jitter, etc.
    self.edge_info  = edge_info
    # Links as source->dest pairs mapped to a link type.
    self.links      = dict()
    # Characteristics for each link type.
    self.link_characteristics = dict()
    # Link type counter.
    self.link_type_number = 0


  def create_links(self, nodes, links: dict) -> None:
    '''
    Create the links with the right characteristics and proper names.

    nodes:  The nodes in the topology, as nameservers, etc.
    links:  The link definitions (source->dest, etc.).
    '''
    self.nodes  = nodes
    for source_dest, default_info in links.items():
      source, dest = source_dest.split("->")
      link_name = f"{source}->{dest}"
      info = self.edge_info.get(f"{link_name}", None)
      if info is None:
        logger.info(f"Did not find {link_name}, reversing direction.")
        link_name = f"{dest}->{source}"
        info = self.edge_info.get(f"{link_name}", None)
      link = ParameterizedLink(info)
      link_type = self.get_link_type(link)
      if not link_type in self.link_characteristics:
        self.link_characteristics[link_type]  = link
      self.links[f"{link_name}"] = link_type



  def get_link_type(self, link) -> str:
    """
    Get the link type for a link.  If this is a new type, create a new name for
    it.

    link: The link for which a type is needed.
    """
    # Look through the link characteristics,
    for link_type, existing_link in self.link_characteristics.items():
      # If one like this already exists, use that type.
      if existing_link.is_equal_to(link):
        return link_type

    # Did not find a link with the same characteristics; make a new type.
    link_type = f"LinkType-{self.link_type_number}"
    self.link_type_number += 1
    return link_type
       

  def to_string(self) -> str:
    """
    Create a printable string for this object.

    Return the printable string of the object.
    """
    s  = "ParameterizedNetwork:\n"
    s += f"Nodes: {self.nodes}\n"
    s += f"Links: {self.links}\n"
    s += f"Link characteristic:\n"
    for  link, characteristics in self.link_characteristics.items():
      s += f"{link} -> {characteristics.to_string()}\n"
    return s


  def to_maude_network(self) -> str:
    '''
    Turn object to maude code.
    Return the string of the maude code to place in experiment file.
    '''
    maude_str   = " --- Link Characteristic definitions\n"
    for link_type, link in self.link_characteristics.items():
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
      try:
        source_address  = list(map(lambda node: node.address, filter(
          lambda source_addr: source_str in source_addr.address, self.nodes)))[0]
        dest_address  = list(map(lambda node: node.address, filter(
          lambda dest_addr: dest_str in dest_addr.address, self.nodes)))[0]
        maude_str += f"  aaa({dest_address},{source_address},{link_type})\n"
      except Exception as e:
        print(f"Error {e}")
    maude_str += "  .\n"
    return maude_str



class ParameterizedLink:
  '''
  The class for defining parameterized links.
  '''
  def __init__(self, link_info) -> None:
    '''
    Constructor.
    link_info: The DiGraph edges with data.
    '''
    if link_info is None:
      # Default link, when nothing is specified.
      self.delayType  = "Constant"
      self.delayMean  = 0.
      self.delayStd   = 0.
      self.delayConst = 0.002
      self.noiseMin   = 0.
      self.noiseMax   = 0.00001

      self.canDrop    = False
      self.dropP      = 0.
      return

    self.delayStd   = link_info.get("jitter", 0.) * 0.667
    self.delayType  = "Constant" if self.delayStd == 0. else "Normal"
    # T&E V1 used RTT times, this is compatible with V2.
    self.delayMean  = 0. if self.delayStd == 0. else link_info.get("latency", 0.005) 
    self.delayConst = link_info.get("latency", 0.005) if self.delayStd == 0. else 0.
    self.noiseMin   = 0.
    self.noiseMax   = 0.00001 if self.delayStd == 0. else 0.

    self.dropP      = link_info.get("loss", 0.)
    self.canDrop    = self.dropP != 0.


  def to_string(self) -> str:
    """
    Create a printable string for this object.

    Return the printable string of the object.
    """
    s  = f"Chars: Type {self.delayType}, "
    s += f"Delay: {self.delayConst}, "
    s += f"NoiseMin: {self.noiseMin}, "
    s += f"NoiseMax: {self.noiseMax}, "
    s += f"Mean: {self.delayMean}, "
    s += f"Std: {self.delayStd}, "
    s += f"canDrop: {self.canDrop}, "
    s += f"prob: {self.dropP}"
    return s


  def is_equal_to(self, link):
    """
    Compare a link to this object.

    link: The link to which to compare.
    """
    if self.delayType == "Constant":
      delay_sameness = link.delayType == self.delayType and \
        link.delayConst == self.delayConst and \
        link.noiseMin == self.noiseMin and \
        link.noiseMax == self.noiseMax
    else:
      delay_sameness = link.delayType == self.delayType and \
        link.delayMean == self.delayMean and \
        link.delayStd == self.delayStd

    if self.canDrop:
      drop_sameness = link.canDrop == self.canDrop and \
        link.dropP == self.dropP
    else:
      drop_sameness = link.canDrop == self.canDrop

    return delay_sameness and drop_sameness


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

