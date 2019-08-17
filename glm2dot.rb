#!/usr/bin/env ruby

# This software is (c) 2012 Michael A. Cohen
# It is released under the simplified BSD license, which can be found at:
# http://www.opensource.org/licenses/BSD-2-Clause
# 
# glm2dot.rb converts gridlab-d feeder model (.glm) files into graphviz DOT
# (.dot) files for visual rendering. Specifically it was designed
# for and works well with the official "taxonomy" feeders at
# http://sourceforge.net/apps/mediawiki/gridlab-d/index.php?title=Feeder_Taxonomy
# (as of 2012-02-09)
# If you have custom feeder models that are similar in syntax, it will likely
# work well with yours as well, but the parser is not terribly robust at this
# stage and will not handle all legal syntax.  In particular, it doesn't understand
# nesting a child object under its parent.
#
# To convert my_feeder.glm to my_feeder.dot, just do:
# $ ruby glm2dot.rb path/to/my_feeder.glm path/to/my_feeder.dot "Your name here"
#
# to render your graph, make sure you have graphviz installed,
# then do something like:
# $ neato my_feeder.dot -Tpdf -omy_feeder.pdf
#
# Note that the xlabel attribute was introduced in graphviz 2.29 and won't work
# with earlier versions.
#
# Graphviz supports *many* output formats besides pdf; for more options,
# see the graphviz documentation at http://graphviz.org

# some string helper functions
class String
  # take a string like "my_class" and make it into "MyClass"
  def to_class_name
    self.split('_').each{|w| w.capitalize!}.join('')
  end
  
  # take a string like "R1-12-47-1_tm_598;" and make it into "tm598"
  # (makes node identifiers more succinct)
  def core
    splits = self.split('-')
    #splits[-2] + splits[-1]
    splits.join('_')
  end
end

# GrabInfo is mixed in to the node types that scale their visual area
# based on their constant (real) power draw
# See, e.g. class Load below
module GrabInfo
  # number of output inches per W**(1/2) of load
  LOAD_SCALE = 0.002
  
  # Returs nil if this node has no real power load
  def size_from_power
    pow = 0
    # note that for multi-phase loads, we just sum the real power draw
    # across the phases
    each {|k, v| pow += v.to_c.abs if k.to_s =~ /^(constant_)?power(_12)?/}
    pow == 0 ? nil : (Math.sqrt(pow) * LOAD_SCALE).to_s
  end
  
  def size_from_area
    area = 0
    each {|k, v| area += v.to_f if k.to_s =~ /^floor_area/}
    area == 0? nil : (Math.sqrt(area) * LOAD_SCALE).to_s
  end
  
  def get_groupid
    groupid = nil
    each {|k, v| groupid = v.to_s if k.to_s =~ /^groupid/}
    groupid
  end
  
end

# GLMConverter is the main class that loops through the input file, farms
# out the parsing of various objects, then coordinates the writing of the
# .dot file.
class GLMConverter
  VERSION = '0.1'
  
  def initialize(infilename, outfilename, creator = '')
    @infilename = infilename
    @outfilename = outfilename
    @creator = creator.nil? || creator.empty? ? '[unknown]' : creator
    # note configs aren't used for anything currently
    @lists = {:nodes => [], :edges => [], :configs => []}
  end
  
  # Parse the .glm input file into ruby objects
  def parse
    infile = File.open @infilename
    
    while l = infile.gets do  
      if l =~ /^object/        
        # we've found a line like "object capacitor:2076 {"
        # the index is "capacitor:2076"
        index = l.split[1].chomp(';')
        # the type is "capacitor"
        type = index.split(':')[0].chomp('{')
        
        # gather up all the lines of input that define the current object
        # into lines
        lines = []
        lines << (l = infile.gets) until l =~ /^\s*\}/
        # remove the last line, "}"
        lines.pop
        
        # see if there's a class (defined below) that corresponds to the type
        # of object we've found
        klass = Module.const_get(type.to_class_name) rescue nil
        if klass.is_a?(Class) && klass.ancestors.include?(GLMObject)
          # if there is a class corresponding to the current object type,
          # instantiate it and let it initialize itself based on #lines
          puts "Parsing #{index}"
          obj = klass.new lines
          obj[:name] = index if obj[:name].nil?
          
          # add the new object to the appropriate list (:nodes, :edges, etc.)
          @lists[obj.list] << obj
          
          # if the new object has a "parent" attribute, create and save
          # a dummy edge linking the parent to the new object
          if obj[:parent]
            dummy = Edge.dummy obj[:parent], obj[:name]
            @lists[:edges] << dummy
          end
        else
          # if there's no class corresponding to the object type, skip it
          puts "Ignoring #{index}"
        end
      end
    end
    
    infile.close
  end
  
  # write out a DOT file based on the parsed objects
  def write
    outfile = File.open @outfilename, 'w'
    feeder_name = File.basename @infilename, '.glm'
    outfile.puts 'graph "' + feeder_name + '" {'
    outfile.puts "label=\"Feeder #{feeder_name} Scale: 1in = #{1/Edge::LEN_SCALE}ft Created by #{@creator} using glm2dot.rb version #{VERSION} on #{Time.now}\";"
    outfile.puts 'fontsize="24";'
    outfile.puts 'node [fontname="Helvetica", fontcolor="/x11/gray50", fontsize="8", colorscheme="accent8"];'
    outfile.puts 'edge [colorscheme="accent8"];'
    @lists[:nodes].each {|n| outfile.puts n.to_s}
    @lists[:edges].each {|e| outfile.puts e.to_s}
    outfile.puts '}'
    outfile.close
  end
end

# base class for any object we care about in a .glm file
# GLMObject basically just parses lines from the input file into
# a key/value in its Hash-nature
# Child classes are expected minimally to specify a #props method
# that generates a hash of the DOT properties for the object and a
# #to_s method that returns the entire DOT file line for the object
class GLMObject < Hash
  def initialize(lines) 
    lines.each do |l|
      s = l.strip.chomp(';').split
      
      if !s.empty?
        prop_name = s.shift.strip
        prop_val = s.join
        # for some properties, we want to "tweak" the value from what's in
        # the file. If we define a method with the right name (like tweak_name)
        # then it will be called to modify the property's value before continuing
        method_sym = ("tweak_" + prop_name).to_sym
        self[prop_name.to_sym] = respond_to?(method_sym) ? send(method_sym, prop_val) : prop_val
      end
      
    end
  end
  
  # The following tweak methods "core" node names so they are more succinct
  # (see the String helper methods above)
  # If you prefer the full-length node names, just comment these out!
  
  def tweak_name(n)
    n.core
  end
  
  def tweak_to(t)
    t.core
  end
  
  def tweak_from(f)
    f.core
  end
  
  def tweak_parent(p)
    p.core
  end
end

# Base class for all GLMObjects that are treated as nodes
# Note that "node" is an actual, instantiated object type in .glm.
# In this script, Node also serves as a generic base class for other node-like
# objects.
class Node < GLMObject
  def list
    :nodes
  end
  
  # The default Node generates properties causing it to render as a point
  # If the node is the SWING bus, it renders more visibly
  # Of course, descendants of this class can override this method to cause
  # a different rendering for different kinds of nodes
  def props
    p = {'label' => '',
         'xlabel' => self[:name],
         'shape' => 'point',
         'style' => 'filled'
    }
    if self[:bustype] == 'SWING'
      p.merge!({'shape' => 'doubleoctagon', 
                'width' => '0.1',
                'height' => '0.1',
                'color' => '6'
      })
    end
    p
  end
  
  # The line of DOT code defined by a Node
  def to_s
    s = self[:name] + ' ['
    props.each {|k, v| s += "#{k}=\"#{v}\", "}
    s.chomp(', ') + '];'
  end
end

# base class for all GLMObjects that are treated as edges
class Edge < GLMObject    
  LEN_SCALE = 0.005 # DOT inches per GLM foot
  MIN_LEN = '0.25' # minimum length of any edge in DOT inches (for visibility)
  # edges with specified lengths are "weighted" heavier to ensure that graphviz
  # doesn't distort their lengths too liberally.
  WEIGHT_FOR_SPECIFIED = '5'
  
  def list
    :edges
  end
  
  # create a dummy edge; for linking parents to children
  def self.dummy(from, to)
    e = self.new []
    e[:from] = from
    e[:to] = to
    e
  end
  
  def props
    if self[:length].nil?
      {"len" => MIN_LEN}
    else
      { "len" => [(self[:length].to_f * LEN_SCALE).to_s, MIN_LEN].max.to_s,
        "weight" => WEIGHT_FOR_SPECIFIED
      }
    end
  end
  
  # The line of DOT code defined by an Edge
  def to_s
    s = "#{self[:from]} -- #{self[:to]} ["
    props.each {|k, v| s += "#{k}=\"#{v}\", "}
    s.chomp(', ') + '];'
  end
end

class GLMConfig < GLMObject
  def list
    :configs
  end
end

# Hereafter are classes that correspond to specific types of GLM objects we
# care to have in our graph.  For the most part they just override #props to
# provide a different visual rendering for different types of nodes/edges.
# Note though that many of them use a "super.merge(...)" convention in their
# #props method, which effectively allows them to inherit the DOT properties
# of the basic Node/Edge/GLMConfig while overriding some of them.

class Regulator < Edge
  def props
    super.merge({'color' => '1:8:1', 'penwidth' => '3'})
  end 
end

class RegulatorConfiguration < GLMConfig
end
  
class Capacitor < Node
  def props
    super.merge({
      'shape' => 'doublecircle',
      'width' => '0.2',
      'height' => '0.2',
      'fillcolor' => '1'
    })
  end  
end

class Fuse < Edge
  def props
    super.merge({'color' => '6', 'penwidth' => '5'})
  end  
end

class LineConfiguration < GLMConfig
end

class Load < Node
  include GrabInfo
  
  def props
    p = super.merge({
      'shape' => 'square',
      'fillcolor' => '2'
    })
    size = size_from_power
    p.merge({'width' => size, 'height' => size})
  end  
end

class Meter < Node
  def props
    super.merge({
      'shape' => 'circle',
      'width' => '0.2',
      'height' => '0.2',
      'fillcolor' => '2'
    })
  end  
end

class OverheadLine < Edge
  def props
    super.merge({'color' => '5', 'penwidth' => '2'})
  end  
end

class Recloser < Edge
  def props
    super.merge({'color' => '6:8:6', 'penwidth' => '3'})
  end  
end

class Switch < Edge
  def props
    super.merge({'color' => '4', 'penwidth' => '5'})
  end 
end

class Transformer < Edge
  def props
    super.merge({'color' => '1', 'penwidth' => '5'})
  end 
end

class TransformerConfiguration < GLMConfig
end

class TriplexLineConfiguration < GLMConfig
end

class TriplexLine < Edge
  def props
    super.merge({'color' => '8'})
  end  
end

class TriplexMeter < Node
  include GrabInfo
  
  def props
    groupid = get_groupid
    
    if groupid == 'Commercial_Meter'
      super.merge({
      'shape' => 'circle',
      'width' => '0.15',
      'height' => '0.15',
      'fillcolor' => '2'
    })
    else
      super.merge({
        'shape' => 'circle',
        'width' => '0.15',
        'height' => '0.15',
        'fillcolor' => '3'
    })
    end
  end
end

class TriplexNode < Node
  include GrabInfo
  
  def props
    p = super
    size = size_from_power
    
    if size == nil
      p.merge!({'shape' => 'triangle',
                'fillcolor' => '7',
                'height' => 0.15,
                'width' => 0.15
      })
    else
      p.merge!({'shape' => 'house',
                'fillcolor' => '4',
                'height' => size,
                'width' => size
      })
    end
    p
  end
end


class House < Node
  include GrabInfo
  
  def props
    p = super
    size = size_from_area
    groupid = get_groupid
    unless size.nil?
      if groupid == 'Commercial'
        p.merge!({'shape' => 'invtriangle',
                  'fillcolor' => '2',
                  'height' => size,
                  'width' => size
        })
      else
        p.merge!({'shape' => 'house',
                  'fillcolor' => '4',
                  'height' => size,
                  'width' => size
        })
      end
    end
    p
  end
end





class UndergroundLine < Edge
  def props
    super.merge({'color' => '7', 'penwidth' => '2'})
  end  
end

# Ignoring Recorders for now because when their parent is an edge (e.g. a
# regulator) it confuses things and you get a floating, disconnected recorder +
# fake node.
#
# I'm sure this can be fixed, but right now in the context of this script,
# children aren't linked directly to their parents so it's hard for a node to know
# when it has this problem.
#
# class Recorder < Node
#   def initialize(lines)
#     super lines
#     self[:name] = "recorder_for_#{self[:parent]}" if self[:name].nil?
#   end
#  
#   def props
#     super.merge({
#       'shape' => 'note',
#       'width' => '0.2',
#       'height' => '0.2',
#       'fillcolor' => 'yellow'
#     })
#   end  
# end

# Main execution of the script.  Just grabs the parameters and tells
# GLMConverter to do its thing
infilename = ARGV[0]
outfilename = ARGV[1]
creator = ARGV[2]

converter = GLMConverter.new infilename, outfilename, creator
converter.parse
converter.write