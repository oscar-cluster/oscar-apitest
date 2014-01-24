"""
This file contains an implementation of a directed graph class.
"""
#############################################################################
#
#     This Cplant(TM) source code is the property of Sandia National
#     Laboratories.
#
#     This Cplant(TM) source code is copyrighted by Sandia National
#     Laboratories.
#
#     The redistribution of this Cplant(TM) source code is subject to the
#     terms of the GNU Lesser General Public License
#     (see cit/LGPL or http://www.gnu.org/licenses/lgpl.html)
#
#     Cplant(TM) Copyright 1998, 1999, 2000, 2001, 2002 Sandia Corporation.
#     Under the terms of Contract DE-AC04-94AL85000, there is a non-exclusive
#     license for use of this work by or on behalf of the US Government.
#     Export of this program may require a license from the United States
#     Government.
#
#############################################################################


from Queue import Queue

class digraph:
    """ A directed graph class. """

    #---------------------------------------
    # constructor
    #---------------------------------------
    def __init__(self):
        """ Initialize the digraph. """
        self.debug = False
        self.name  = "digraph"
        self.eid   = 0
        self.V     = {}      # Vertex List  (in_edges, out_edges, data)
        self.E     = {}      # Edge list
        self._V    = {}      # hidden vertices
        self._E    = {}      # hidden edges

    #----------------------------------------
    # DEBUGGING
    #----------------------------------------
    def debug_on(self):
        """ Turn debugging mode on. """
        self.debug = True
    def debug_off(self):
        """ Turn debugging mode off. """
        self.debug = False
    def set_name(self,name):
        """ Assign a name to the graph. """
        self.name = name
    def get_name(self):
        """ Returns the graph name. """
        return self.name

    #----------------------------------------
    # add_vertex()
    #----------------------------------------
    def add_vertex(self, vid, data=None):
        """ Add a vertex to G with optional payload """
        if self.debug: print "[->] %s.add_vertex(%s,%s)"%(self.name,`vid`,`data`)
        if (not self.V.has_key(vid)) and (not self._V.has_key(vid)):
            self.V[vid] = ([],[],data)
        else:
            print "graph.add_vertex() error:: vertex \"%s\" already exists!"%(str(vid))

    #----------------------------------------
    # del_vertex()
    #----------------------------------------
    def del_vertex(self, vid):
        """ Delete the vertex, vid, and all incoming and outgoing edges from G."""
        if self.debug: print "[->] %s.del_vertex(%s)"%(self.name,`vid`)
        edges = map(None, self.V[vid])
        eid_i = edges[0][:]
        eid_o = edges[1][:]
        for edge in eid_i:
            self.del_edge(edge)
        for edge in eid_o:
            self.del_edge(edge)
        del self.V[vid]

    #----------------------------------------
    # del_vertices()
    #----------------------------------------
    def del_vertices(self, vid_list):
        """ Deletes all vertices in G from the list vid_list """
        if self.debug: print "[->] %s.del_vertices(%s)"%(self.name,`vid_list`)
        for vid in vid_list:
            self.del_vertex(vid)

    #----------------------------------------
    # del_all_vertices()
    #----------------------------------------
    def del_all_vertices(self):
        """ Delete all visible vertices from the digraph. """
        if self.debug: print "[->] %s.del_all_vertices()"%(self.name)
        for vid in self.V.keys():
            self.del_vertex(vid)

    #----------------------------------------
    # del_all_edges()
    #----------------------------------------
    def del_all_edges(self):
        """ Delete all visible edges from the digraph. """
        if self.debug: print "[->] %s.del_all_edges()"%(self.name)
        for eid in self.E.keys():
            self.del_edge(eid)

    #----------------------------------------
    # clear()
    #----------------------------------------
    def clear(self):
        """ Delete all vertices and edges in G. """
        if self.debug: print "[->] %s.clear()"%(self.name)
        self.unhide_all()
        self.del_all_edges()
        self.del_all_vertices()
        self.eid = 0
        self.debug_off()
        
    #----------------------------------------
    # hide_vertex()
    #----------------------------------------
    def hide_vertex(self, vid):
        """ Hides vertex, vid, and incoming/outgoing edges from the visible digraph. """
        if self.debug: print "[->] %s.hide_vertex(%s)"%(self.name,`vid`)
        in_edges  = self.get_eid_list_by_dest(vid)
        out_edges = self.get_eid_list_by_source(vid)
        self._V[vid] = (self.V[vid],in_edges,out_edges)
        for edge in in_edges:
            self.hide_edge(edge)
        for edge in out_edges:
            self.hide_edge(edge)
        self.del_vertex(vid)

    #----------------------------------------
    # hide_edge(eid)
    #----------------------------------------
    def hide_edge(self, eid):
        """ Hides an edge from the visible digraph."""
        self._E[eid] = self.E[eid]
        self.del_edge(eid)

    #----------------------------------------
    # hide_edge_By_vid(v1id,v2id)
    #----------------------------------------
    def hide_edge_by_vid(self, v1id, v2id):
        """ Hides an edge, given the vertex ids of its head and tail. """
        edge_list = self.get_eid_list(v1id, v2id)
        for edge in edge_list:
            self.hide_edge(edge)

    #----------------------------------------
    # unhide_vertex(vid)
    #----------------------------------------
    def unhide_vertex(self, vid):
        """ Unhide a vertex, given the vertex id. """
        if self.debug: print "[->] %s.unhide_vertex(%s)"%(self.name,`vid`)
        if self._V.has_key(vid):
            self.V[vid] = self._V[vid][0]
            for eid in self._V[vid][1]:
                self.unhide_edge(eid)
            for eid in self._V[vid][2]:
                self.unhide_edge(eid)
            del self._V[vid]

    #----------------------------------------
    # unhide_edge(eid)
    #----------------------------------------
    def unhide_edge(self, eid):
        """ Unhide an edge, given its edge id."""
        if self.debug: print "[->] %s.unhide_edge(%s)"%(self.name,`eid`)
        if self._E.has_key(eid):
            edge = self._E[eid]
            self.E[eid] = edge
            self.V[edge[0]][1].append(eid)
            self.V[edge[1]][0].append(eid)
            del self._E[eid]
            
    #----------------------------------------
    # unhide_edge_by_vid(v1id,v2id)
    #----------------------------------------
    def unhide_edge_by_vid(self, v1id,v2id):
        """ Unhide an edge, given the vertex ids of its head and tail. """
        if self.debug: print "[->] %s.unhide_edge_by_vid(%s,%s)"%(self.name,`v1id`,`v2id`)
        edge_list = self.get_hidden_eid_list(v1id,v2id)
        for edge in edge_list:
            self.unhide_edge(edge)
        
    #----------------------------------------
    # unhide_all()
    #----------------------------------------
    def unhide_all(self):
        """ Unhide all vertices and edges in the digraph. """
        if self.debug: print "[->] %s.unhide_all()"%(self.name)
        for vid in self._V.keys():
            self.unhide_vertex(vid)
        for eid in self._E.keys():
            self.unhide_edge(eid)

    #----------------------------------------
    # number_of_vertices()
    #----------------------------------------
    def number_of_vertices(self):
        """ Returns the number of visible vertices in the digraph. """
        return len(self.V)

    #----------------------------------------
    # number_of_edges()
    #----------------------------------------
    def number_of_edges(self):
        """ Returns the number of visible edges in the digraph. """
        return len(self.E)

    #----------------------------------------
    # number_of_hidden_vertices()
    #----------------------------------------
    def number_of_hidden_vertices(self):
        """ Returns the number of hidden vertices in the digraph. """
        return len(self._V)

    #----------------------------------------
    # number_of_hidden_edges()
    #----------------------------------------
    def number_of_hidden_edges(self):
        """ Returns the number of hidden edges in the digraph. """
        return len(self._E)

    #----------------------------------------
    # vertex_list()
    #----------------------------------------
    def vertex_list(self):
        """ Returns the list of nodeids of all unhidden nodes in G """
        return self.V.keys()

    #----------------------------------------
    # edge_list()
    #----------------------------------------
    def edge_list(self):
        """ Returns the list of eid's of all unhidden edges in G """
        return self.E.keys()

    #----------------------------------------
    # has_vertex(vid)
    #----------------------------------------
    def has_vertex(self, vid):
        """ Does vid exist in G?  Returns True or False """
        if self.debug: print "[->] %s.has_vertex(%s)"%(self.name,`vid`)
        return self.V.has_key(vid)

    def get_vertex(self, vid):
        """ Returns the vertex given by `vid` """
        if self.debug: print "[->] %s.get_vertex(%s)"%(self.name,`vid`)
        if self.has_vertex(vid):
            return self.V[vid]
        else:
            return None

    def get_vertex_data(self, vid):
        """ Returns the vertex data attached to vertex `vid` """
        if self.debug: print "[->] %s.get_vertex_data(%s)"%(self.name,`vid`)
        if self.has_vertex(vid):
            return self.get_vertex(vid)[2]
        else:
            return None

    #----------------------------------------
    # has_edge(v1id,v2id)
    #----------------------------------------
    def has_edge(self, v1id, v2id):
        """ Does the edge v1id -> v2id exist? Returns True or False """
        if self.debug: print "[->] %s.has_edge(%s,%s)"%(self.name,`v1id`,`v2id`)
        return (len(self.get_eid_list(v1id,v2id)) > 0)

    #----------------------------------------
    # add_edge(v1id,v2id,[data])
    #----------------------------------------
    def add_edge(self, v1id, v2id, data=None):
        """ Add an edge from v1id -> v2id into G. data is optional (edgeweight) """
        if self.debug: print "[->] %s.add_edge(%s,%s, %s)"%(self.name,`v1id`,`v2id`,`data`)
        eid = self.eid
        self.eid += 1
        self.E[eid] = (v1id, v2id, data)
        m1d = map(None, self.V[v1id])
        m2d = map(None, self.V[v2id])
        m1d[1].append(eid)
        m2d[0].append(eid)
        return eid

    #----------------------------------------
    # del_edge_by_vid(v1id,v2id)
    #----------------------------------------
    def del_edge_by_vid(self, v1id, v2id):
        """ Delete an edge from the digraph, given the vertex ids of the head and tail. """
        if self.debug: print "[->] %s.del_edge_by_vid(%s,%s)"%(self.name,`v1id`,`v2id`)
        eid = self.get_eid(v1id,v2id)
        # print eid
        if eid != None:
            self.del_edge(eid)
        else:
            print "del_edge_by_vid(%s,%s) :: Edge does not exist!"%(`v1id`,`v2id`)

    #----------------------------------------
    # del_edge(eid)
    #----------------------------------------
    def del_edge(self, eid):
        """ Delete an edge, given the edge id. """
        if self.debug: print "[->] %s.del_edge(%s)"%(self.name,`eid`)
        if self.E.has_key(eid):
            v1id = map(None, self.E[eid])[0]
            v2id = map(None, self.E[eid])[1]
            v1data = map(None, self.V[v1id])
            v2data = map(None, self.V[v2id])
            v1data[1].remove(eid)
            v2data[0].remove(eid)
            del self.E[eid]
        else:
            print "del_edge(%s) :: no edge exists with that eid!"%(`eid`)

    #----------------------------------------
    # get_eid_list(v1id, v2id)
    #----------------------------------------
    def get_eid_list(self, v1id, v2id):
        """ Returns list of edges going from v1id to v2id """
        if self.debug: print "[->] %s.get_eid_list(%s,%s)"%(self.name,`v1id`,`v2id`)
        eid_list = []
        eid_list = filter( \
            lambda eid: self.E[eid][0]==v1id and self.E[eid][1]==v2id,\
            self.E.keys() )
        return eid_list

    #----------------------------------------
    # get_hidden_eid_list(v1id, v2id)
    #----------------------------------------
    def get_hidden_eid_list(self, v1id, v2id):
        """ Returns list of edges going from v1id to v2id that are hidden """
        if self.debug: print "[->] %s.get_hidden_eid_list(%s,%s)"%(self.name,`v1id`,`v2id`)
        eid_list = []
        eid_list = filter( \
            lambda eid: self._E[eid][0]==v1id and self._E[eid][1]==v2id,\
            self._E.keys() )
        return eid_list

    #----------------------------------------
    # get_eid()
    #----------------------------------------
    def get_eid(self, v1id, v2id):
        """ Return the first edge found from v1id->v2id """
        if self.debug: print "[->] %s.get_eid(%s,%s)"%(self.name,`v1id`,`v2id`)
        eid_list = self.get_eid_list(v1id, v2id)
        if len(eid_list):  return eid_list[0]
        else:              return None

    #----------------------------------------
    # get_eid_list_by_source()
    #----------------------------------------
    def get_eid_list_by_source(self, v1id):
        """ Return a list of edges whose source vertex id is specified by v1id. """
        if self.debug: print "[->] %s.get_eid_list_by_source(%s)"%(self.name,`v1id`)
        eid_list = filter( lambda eid : self.E[eid][0]==v1id, self.E.keys() )
        return eid_list

    #----------------------------------------
    # get_hidden_eid_list_by_dest()
    #----------------------------------------
    def get_hidden_eid_list_by_source(self,v1id):
        """ Return a list of hidden edge ids whose source vertex id
        is specified by v1id """
        if self.debug: print "[->] %s.get_hidden_eid_list_by_source(%s)"%(self.name,`v1id`)
        eid_list = filter( lambda eid : self._E[eid][0]==v1id, self.E.keys() )
        return eid_list

    #----------------------------------------
    # get_eid_list_by_dest()
    #----------------------------------------
    def get_eid_list_by_dest(self, v2id):
        """ Return a list of visible edge ids whose destination vertex id
        is specified by v2id.
        """
        if self.debug: print "[->] %s.get_eid_list_by_dest(%s)"%(self.name,`v2id`)
        eid_list = filter( lambda eid : self.E[eid][1]==v2id, self.E.keys() )
        return eid_list
    
    #----------------------------------------
    # get_hidden_eid_list_by_dest()
    #----------------------------------------
    def get_hidden_eid_list_by_dest(self, v2id):
        """ Return a list of hidden edge ids whose destination vertex id
        is specified by v2id.
        """
        if self.debug: print "[->] %s.get_hidden_eid_list_by_dest(%s)"(self.name,`v2id`)
        eid_list = filter( lambda eid : self._E[eid][1]==v2id,self.E.keys() )
        return eid_list

    #----------------------------------------
    def get_edge_dest(self, eid):
        """ Returns the vid of destination vertex for edge. """
        return self.E[eid][1]
    
    #----------------------------------------
    def get_edge_source(self,eid):
        """ Returns the vid of the source vertex for an edge. """
        return self.E[eid][0]

    #----------------------------------------
    def get_edge_data(self, eid):
        """ Returns the data (edgeweight) of an edge. """
        return self.E[eid][2]

    #----------------------------------------
    # indegree(vid)
    #----------------------------------------
    def indegree(self, vid):
        """ Return the count of incident edges on VID. """
        if self.V.has_key(vid):
            return len( self.V[vid][0] )
        else:
            return 0

    #----------------------------------------
    # outdegree(vid)
    #----------------------------------------
    def outdegree(self, vid):
        """ Return the count of outgoing edges from VID. """
        if self.V.has_key(vid):
            return len( self.V[vid][1] )
        else:
            return 0
        
    #----------------------------------------
    # degree(vid)
    #----------------------------------------
    def degree(self, vid):
        """ Return the total degree (indegree+outdegree) of a vertex. """
        return self.indegree(vid)+self.outdegree(vid)

    
    #----------------------------------------
    # dump_graphviz()
    #----------------------------------------
    def dump_graphviz(self):
        """ return a string with the graph info in Graphviz .dot format """
        s = "digraph \"%s\" {\n"%(self.name)
        for vid in self.V.iterkeys():
            eid_list = self.get_eid_list_by_source(vid)
            for eid in eid_list:
                s += "\"%s\" -> \"%s\";\n"%(vid,self.get_edge_dest(eid))
        s += "};"
        return s

    #----------------------------------------
    # __str__()
    #----------------------------------------
    def __str__(self):
        """ Return a compact string representation of the digraph. """
        s = "Graph: %s\n"%(`self.name`)
        for vid in self.V.iterkeys():
            s += "  %-20s\t(%10s) -> { "%(`vid`,`self.V[vid][2]`)
            for eid in self.get_eid_list_by_source(vid):
                s += "%s(%s), "%(`self.get_edge_dest(eid)`, `self.get_edge_data(eid)`)
            s += '}\n'
        return s

    #----------------------------------------
    # pretty_print()
    #----------------------------------------
    def pretty_print(self):
        """ Return a string based representation of the digraph. """
        s = ""
        for vid in self.V.iterkeys():
            s += "V: %s\n"%(`vid`)

            s += "   in ["
            eid_list = self.get_eid_list_by_dest(vid)
            for eid in eid_list:
                s += " %s(%s)"%(`self.get_edge_source(eid)`,`self.get_edge_data(eid)`)
            s += "]\n"
        return s


    #----------------------------------------
    # topological_sort()
    #----------------------------------------
    def topological_sort(self):
        """ Return a list of vertex ids, sorted topologically. """
        if self.debug: print "[->] %s.topological_sort()"%(self.name)
        v_topolist = []
        Q          = Queue()
        v_indegree = {}
        for vid in self.V.iterkeys():
            indeg = self.indegree(vid)
            if indeg==0:
                Q.put(vid)
            else:
                v_indegree[vid] = indeg
        while not Q.empty():
            vid = Q.get()
            v_topolist.append(vid)
            out_edges = self.get_eid_list_by_source(vid)
            for eid in out_edges:
                dest = self.get_edge_dest(eid)
                v_indegree[dest] -= 1
                if v_indegree[dest]==0:
                    Q.put(dest)
        if len(v_topolist) != len(self.V):
            print "WARNING: digraph '%s' appears to be cyclic!"%(self.name)
        return v_topolist




#----------------------------------------------------------------------------------
# Testing function.  This is executed if we run python digraph.py
#----------------------------------------------------------------------------------
if __name__ == "__main__":
    print "Testing digraph module"

    G = digraph()
    G.set_name("G")
    G.add_vertex('a')
    G.add_vertex('b')
    G.add_vertex('c')
    G.add_vertex('d')
    G.add_vertex('e')
    G.add_vertex('f')
    G.add_vertex('g')
    G.add_edge('a','b')
    G.add_edge('a','c')
    G.add_edge('b','d')
    G.add_edge('b','e')
    G.add_edge('c','f')
    G.add_edge('c','g')
    G.add_edge('g','b')
    G.add_edge('e','f')

    print G.__str__()
    print "Topological Order:", G.topological_sort()
    print ""

    G_2 = digraph()
    G_2.set_name("G_2")
    G_2.add_vertex('a')
    G_2.add_vertex('b')
    G_2.add_vertex('c')
    G_2.add_vertex('d')
    G_2.add_edge('a','b')
    G_2.add_edge('a','c')
    G_2.add_edge('c','b')
    G_2.add_edge('c','d')
    G_2.add_edge('b','d')


    print G_2.__str__()
    print "Topological order:", G_2.topological_sort()
    print ""

#EOF
