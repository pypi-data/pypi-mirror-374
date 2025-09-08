"""Visualisation helpers for note relationships."""

import json


class GraphExporter:
    """Export note graphs for visualisation."""

    @staticmethod
    def export_to_json(vault: "Vault", output_path: str | None = None) -> str:
        """Export vault graph to JSON format compatible with D3.js.

        Args:
            vault: The vault to export
            output_path: Optional path to save the JSON file

        Returns:
            JSON string
        """
        nodes = []
        links = []
        node_indices = {}

        # Create nodes
        for i, note in enumerate(vault.notes):
            node_data = {
                "id": note.name,
                "index": i,
                "tags": [tag.name for tag in note.tags],
                "wordCount": len(note.content.split()),
                "hasDataview": note.has_dataview,
            }
            nodes.append(node_data)
            node_indices[note.name] = i

        # Create links
        for note in vault.notes:
            source_idx = node_indices[note.name]
            for link in note.wikilinks:
                if link.target in node_indices:
                    target_idx = node_indices[link.target]
                    links.append({"source": source_idx, "target": target_idx, "value": 1})

        graph_data = {"nodes": nodes, "links": links}

        json_str = json.dumps(graph_data, indent=2)

        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(json_str)

        return json_str

    @staticmethod
    def export_to_gephi(vault: "Vault", nodes_path: str, edges_path: str) -> None:
        """Export vault graph to CSV files for Gephi.

        Args:
            vault: The vault to export
            nodes_path: Path for nodes CSV file
            edges_path: Path for edges CSV file
        """
        import csv

        # Export nodes
        with open(nodes_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Id", "Label", "WordCount", "Tags", "HasDataview"])

            for note in vault.notes:
                writer.writerow(
                    [
                        note.name,
                        note.name,
                        len(note.content.split()),
                        ";".join(tag.name for tag in note.tags),
                        note.has_dataview,
                    ]
                )

        # Export edges
        with open(edges_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Source", "Target", "Type", "Weight"])

            for note in vault.notes:
                for link in note.wikilinks:
                    if vault.get_note(link.target):
                        writer.writerow([note.name, link.target, "Directed", 1])
