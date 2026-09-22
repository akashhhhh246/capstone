import networkx as nx
from typing import List, Dict, Any, Optional

class GraphBuilder:
    """
    Constructs multi-relational propagation graphs using NetworkX.
    Nodes represent Content, Posts, Synthetic Accounts, Platforms, and Campaigns.
    Edges represent multi-platform interactions and derivation links.
    """

    @classmethod
    def build_networkx_graph(
        cls,
        nodes: List[Dict[str, Any]],
        edges: List[Dict[str, Any]]
    ) -> nx.DiGraph:
        """Construct a NetworkX DiGraph from node and edge dictionaries."""
        G = nx.DiGraph()
        
        for node in nodes:
            node_id = str(node["id"])
            attrs = {k: v for k, v in node.items() if k != "id"}
            G.add_node(node_id, **attrs)

        for edge in edges:
            source = str(edge["source"])
            target = str(edge["target"])
            attrs = {k: v for k, v in edge.items() if k not in ("source", "target")}
            G.add_edge(source, target, **attrs)

        return G

    @classmethod
    def from_campaign_data(
        cls,
        campaign: Dict[str, Any],
        posts: List[Dict[str, Any]],
        events: List[Dict[str, Any]],
        accounts: List[Dict[str, Any]],
        platforms: List[Dict[str, Any]]
    ) -> nx.DiGraph:
        """Build full campaign propagation graph from raw relational entities."""
        G = nx.DiGraph()

        # Add Campaign Root Node
        camp_id = str(campaign["id"])
        G.add_node(
            camp_id,
            type="CAMPAIGN",
            name=campaign.get("name", "Unknown Campaign"),
            status=campaign.get("status", "ACTIVE")
        )

        # Add Platforms and link Campaign -> Platform
        for plat in platforms:
            p_id = str(plat["id"])
            G.add_node(
                p_id,
                type="PLATFORM",
                name=plat.get("name", "Platform"),
                platform_type=plat.get("platform_type", "microblogging")
            )
            # Edge: Campaign -> Platform (DEPLOYED_ON)
            G.add_edge(camp_id, p_id, type="DEPLOYED_ON", label="DEPLOYED_ON")

        # Add Synthetic Accounts and link Platform -> Account
        for acc in accounts:
            a_id = str(acc["id"])
            G.add_node(
                a_id,
                type="SYNTHETIC_ACCOUNT",
                handle=acc.get("pseudonym_handle", "@synth"),
                bot_probability=acc.get("bot_probability", 0.0),
                is_coordinated=acc.get("is_coordinated_actor", False),
                platform_id=str(acc.get("platform_id", ""))
            )
            # Edge: Platform -> Account (HOSTS)
            plat_id = str(acc.get("platform_id", ""))
            if plat_id and plat_id in G:
                G.add_edge(plat_id, a_id, type="HOSTS_ACCOUNT", label="HOSTS")

        # Add Posts and link to accounts
        for post in posts:
            post_id = str(post["id"])
            G.add_node(
                post_id,
                type="POST",
                post_type=post.get("post_type", "ORIGINAL"),
                likes=post.get("likes", 0),
                reshares=post.get("reshares", 0),
                published_at=str(post.get("published_at", "")),
                account_id=str(post.get("account_id", "")),
                platform_id=str(post.get("platform_id", ""))
            )

            # Edge: Account -> Post (POSTED)
            acc_id = str(post.get("account_id", ""))
            if acc_id and acc_id in G:
                G.add_edge(acc_id, post_id, type="POSTED", label="POSTED")

            # Edge: Parent Post -> Child Post (RESHARE / REPLY / QUOTE)
            parent_id = str(post.get("parent_post_id", ""))
            if parent_id and parent_id in G:
                G.add_edge(parent_id, post_id, type=post.get("post_type", "RESHARE"), label=post.get("post_type", "RESHARE"))

        # Add dynamic cross-platform propagation events
        for ev in events:
            src = str(ev.get("source_post_id", ""))
            tgt = str(ev.get("target_post_id", ""))
            ev_type = ev.get("event_type", "CROSS_PLATFORM_SHARE")
            if src and tgt and src in G and tgt in G:
                G.add_edge(src, tgt, type=ev_type, label=ev_type, timestamp=str(ev.get("timestamp", "")))

        return G
