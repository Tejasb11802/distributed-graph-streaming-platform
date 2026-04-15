from neo4j import GraphDatabase

GDS_GRAPH_NAME = "taxi_graph"


class Interface:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password), encrypted=False)
        self._driver.verify_connectivity()

    def close(self):
        self._driver.close()

    # ---------------------------------------------------------
    # helpers
    # ---------------------------------------------------------
    def _ensure_graph(self, session):
        # drop old graph if present (tester calls many times)
        session.run("CALL gds.graph.drop($name, false)", name=GDS_GRAPH_NAME)
        # re-project from stored data
        session.run("""
            CALL gds.graph.project(
              $name,
              'Location',
              {
                TRIP: {
                  type: 'TRIP',
                  orientation: 'NATURAL',
                  properties: ['distance', 'fare']
                }
              }
            )
        """, name=GDS_GRAPH_NAME)

    def _location_name_to_node_id(self, session, loc_name):
        rec = session.run(
            "MATCH (l:Location {name: $name}) RETURN id(l) AS id",
            name=int(loc_name)
        ).single()
        if rec is None:
            raise ValueError(f"Location {loc_name} not found")
        return rec["id"]

    # ---------------------------------------------------------
    # PART 2: PageRank – must return [ {name, score}, {name, score} ]
    # ---------------------------------------------------------
    def pagerank(self, max_iterations, weight_property):
        """
        tester.py expects:
            result = iface.pagerank(...)
            result[0] -> dict for MAX  {name: int, score: float}
            result[1] -> dict for MIN  {name: int, score: float}
        """
        with self._driver.session() as session:
            self._ensure_graph(session)

            # run weighted PageRank
            res = session.run("""
                CALL gds.pageRank.stream($g, {
                    maxIterations: $max_iter,
                    dampingFactor: 0.85,
                    relationshipWeightProperty: $w
                })
                YIELD nodeId, score
                RETURN gds.util.asNode(nodeId).name AS name, score
                ORDER BY score DESC, name ASC
            """, g=GDS_GRAPH_NAME, max_iter=max_iterations, w=weight_property)

            rows = list(res)
            if not rows:
                # return in the expected structure even if empty
                return [
                    {"name": None, "score": 0.0},
                    {"name": None, "score": 0.0},
                ]

            max_row = rows[0]
            min_row = rows[-1]

            # tester compares to ints, so cast
            max_obj = {
                "name": int(max_row["name"]),
                "score": float(max_row["score"]),
            }
            min_obj = {
                "name": int(min_row["name"]),
                "score": float(min_row["score"]),
            }

            return [max_obj, min_obj]

    # ---------------------------------------------------------
    # PART 3: BFS – must return [ {"path": [ {"name": ...}, ... ]} ]
    # ---------------------------------------------------------
    def bfs(self, start_node, last_node):
        """
        tester.py calls:
            result = iface.bfs(159, 212)
            result[0]['path'][0]['name']
        so we MUST return:
            [ { "path": [ {"name": 159}, {"name": ...}, {"name": 212} ] } ]
        """
        with self._driver.session() as session:
            self._ensure_graph(session)

            source_id = self._location_name_to_node_id(session, start_node)
            target_id = self._location_name_to_node_id(session, last_node)

            rec = session.run("""
                CALL gds.bfs.stream($g, {
                    sourceNode: $src,
                    targetNodes: [$tgt]
                })
                YIELD path
                RETURN [n IN nodes(path) | n.name] AS path_names
            """, g=GDS_GRAPH_NAME, src=source_id, tgt=target_id).single()

            if rec is None:
                return []

            path_names = rec["path_names"]  # e.g. [159, ..., 212]

            # build exactly what tester wants
            path_objs = [{"name": int(n)} for n in path_names]

            return [
                {
                    "path": path_objs
                }
            ]
