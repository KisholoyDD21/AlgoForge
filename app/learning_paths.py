"""Data-driven DSA learning tracks built from AlgoForge catalogue metadata.

Tracks only reference AlgoForge's own pattern/topic taxonomy and problem slugs;
no third-party statements, examples, editorials, or tests are mirrored here.
"""
from __future__ import annotations

LEARNING_PATHS = [
    {
        "slug": "dsa-foundations",
        "name": "DSA Foundations",
        "level": "Beginner → Intermediate",
        "duration": "10–12 weeks",
        "description": "Build a durable foundation in arrays, strings, hashing and the patterns that appear repeatedly in interviews.",
        "outcome": "Recognise common problem shapes and select an appropriate data structure before coding.",
        "modules": [
            {"id": "arrays", "title": "Arrays and traversal", "objective": "Build confidence with indexing, traversal, in-place updates and matrix iteration.", "patterns": ["Arrays", "Array Traversal", "Array Rotation", "Matrix Traversal", "Matrix In-place"], "topics": ["Arrays", "Matrix"], "target": 3, "minutes": 180, "prerequisites": []},
            {"id": "strings", "title": "String processing", "objective": "Use scans, character counts and string invariants to reason about text problems.", "patterns": ["String Scan", "String Processing", "String Algorithms"], "topics": ["String", "Strings"], "target": 2, "minutes": 150, "prerequisites": ["arrays"]},
            {"id": "hashing", "title": "Hash maps and sets", "objective": "Trade memory for fast lookup, counting and prefix-frequency queries.", "patterns": ["Hash Map", "Hash Set", "Frequency Counting"], "topics": ["Hash Map", "Hashing"], "target": 2, "minutes": 180, "prerequisites": ["strings"]},
            {"id": "two-pointers", "title": "Two pointers", "objective": "Maintain a useful invariant while two indices move through a sequence.", "patterns": ["Two Pointers", "Fast & Slow Pointers"], "topics": ["Two Pointers"], "target": 2, "minutes": 150, "prerequisites": ["arrays"]},
            {"id": "sliding-window", "title": "Sliding window", "objective": "Maintain a contiguous range efficiently instead of recomputing every range.", "patterns": ["Sliding Window"], "topics": ["Sliding Window"], "target": 2, "minutes": 150, "prerequisites": ["two-pointers", "hashing"]},
            {"id": "binary-search", "title": "Binary search", "objective": "Prove a monotonic search boundary and reduce candidate space safely.", "patterns": ["Binary Search", "Modified Binary Search", "Binary Search on Answer"], "topics": ["Binary Search"], "target": 2, "minutes": 180, "prerequisites": ["arrays"]},
            {"id": "stacks", "title": "Stacks and monotonic stacks", "objective": "Model nested structure and next-greater or next-smaller relationships.", "patterns": ["Stack", "Monotonic Stack"], "topics": ["Stack", "Stacks"], "target": 2, "minutes": 150, "prerequisites": ["arrays", "strings"]},
            {"id": "intro-dp", "title": "Dynamic programming introduction", "objective": "Identify states, transitions and base cases; start with one-dimensional DP.", "patterns": ["Kadane's Algorithm", "1D Dynamic Programming", "Dynamic Programming"], "topics": ["Dynamic Programming"], "target": 2, "minutes": 240, "prerequisites": ["hashing", "two-pointers"]},
        ],
    },
    {
        "slug": "graph-algorithms",
        "name": "Graph Algorithms",
        "level": "Intermediate",
        "duration": "6–8 weeks",
        "description": "Move from graph traversal to components, ordering and shortest-path reasoning.",
        "outcome": "Choose BFS, DFS or a shortest-path method based on graph structure and edge weights.",
        "modules": [
            {"id": "graph-traversal", "title": "BFS and DFS", "objective": "Represent a graph and traverse it without revisiting vertices.", "patterns": ["Graph DFS", "Graph DFS / BFS", "Graph Traversal", "Tree DFS", "Tree BFS", "Tree BFS / DFS", "Grid DFS", "Grid DFS / BFS", "Multi-source BFS"], "topics": ["Graphs", "DFS", "BFS"], "target": 3, "minutes": 240, "prerequisites": []},
            {"id": "components", "title": "Connected components", "objective": "Partition a graph or grid into connected regions.", "patterns": ["Graph Traversal", "Graph DFS", "Grid DFS", "Grid DFS / BFS"], "topics": ["Connected Components", "Graphs", "Grid"], "target": 2, "minutes": 180, "prerequisites": ["graph-traversal"]},
            {"id": "topological", "title": "Topological sorting", "objective": "Order vertices in a directed acyclic graph and detect cycles.", "patterns": ["Topological Sort"], "topics": ["Topological Sort", "Graphs"], "target": 1, "minutes": 180, "prerequisites": ["graph-traversal"]},
            {"id": "shortest-paths", "title": "Shortest paths", "objective": "Select BFS for unweighted paths and Dijkstra for non-negative weighted edges.", "patterns": ["Dijkstra", "Dijkstra's Algorithm", "Graph Traversal"], "topics": ["Shortest Path", "Dijkstra"], "target": 2, "minutes": 240, "prerequisites": ["graph-traversal"]},
            {"id": "spanning-trees", "title": "Spanning trees and DSU", "objective": "Connect components efficiently and reason about cycle prevention.", "patterns": ["Greedy / Data Structures"], "topics": ["DSU", "Disjoint Set Union", "Minimum Spanning Tree"], "target": 1, "minutes": 180, "prerequisites": ["components", "shortest-paths"]},
        ],
    },
    {
        "slug": "dynamic-programming",
        "name": "Dynamic Programming",
        "level": "Intermediate → Advanced",
        "duration": "8–10 weeks",
        "description": "Develop a repeatable method for turning recursive choices into memoized and tabulated solutions.",
        "outcome": "Define states and transitions, justify base cases and identify opportunities for space optimisation.",
        "modules": [
            {"id": "dp-foundations", "title": "Recursion and memoization", "objective": "Write a recurrence, identify repeated states and memoize overlapping subproblems.", "patterns": ["Recursion", "1D Dynamic Programming", "Dynamic Programming", "Kadane's Algorithm"], "topics": ["Recursion", "Dynamic Programming"], "target": 2, "minutes": 240, "prerequisites": []},
            {"id": "grid-dp", "title": "Grid and 2D DP", "objective": "Model movement and choices over a two-dimensional state space.", "patterns": ["2D Dynamic Programming", "Grid DP"], "topics": ["Grid DP", "Dynamic Programming"], "target": 1, "minutes": 210, "prerequisites": ["dp-foundations"]},
            {"id": "knapsack", "title": "Knapsack families", "objective": "Distinguish 0/1 and unbounded choices and choose a suitable state dimension.", "patterns": ["Unbounded Knapsack DP", "Dynamic Programming"], "topics": ["Knapsack", "Dynamic Programming"], "target": 1, "minutes": 240, "prerequisites": ["dp-foundations"]},
            {"id": "subsequence", "title": "Subsequence and sequence DP", "objective": "Reason about choices that keep or skip elements while maintaining an optimal state.", "patterns": ["DP + Binary Search", "Dynamic Programming"], "topics": ["Subsequence", "LIS", "Dynamic Programming"], "target": 1, "minutes": 240, "prerequisites": ["knapsack", "grid-dp"]},
            {"id": "advanced-dp", "title": "Advanced state design", "objective": "Explore tree and bitmask state spaces and evaluate state-count complexity.", "patterns": ["Bit DP", "Dynamic Programming"], "topics": ["Tree DP", "Bitmask DP"], "target": 1, "minutes": 300, "prerequisites": ["subsequence"]},
        ],
    },
    {
        "slug": "competitive-programming",
        "name": "Competitive Programming Core",
        "level": "Beginner → Advanced",
        "duration": "10–12 weeks",
        "description": "Build speed without skipping correctness: implementation, mathematics, greedy reasoning and timed practice.",
        "outcome": "Translate constraints into algorithm choices and produce robust contest-ready implementations.",
        "modules": [
            {"id": "implementation", "title": "Implementation and complexity", "objective": "Read constraints, estimate complexity and implement carefully with fast input.", "patterns": ["Implementation", "Fast Input / Implementation", "Simulation", "Array Traversal"], "topics": ["Implementation", "Simulation"], "target": 3, "minutes": 180, "prerequisites": []},
            {"id": "sorting-search", "title": "Sorting and binary search", "objective": "Use sorting to reveal structure and binary search to exploit monotonicity.", "patterns": ["Binary Search", "Modified Binary Search", "Binary Search on Answer"], "topics": ["Sorting", "Binary Search"], "target": 2, "minutes": 210, "prerequisites": ["implementation"]},
            {"id": "greedy", "title": "Greedy reasoning", "objective": "Make a local-choice argument and test the exchange or invariant behind it.", "patterns": ["Greedy", "Greedy + Heap", "Greedy Intervals", "Greedy / Data Structures"], "topics": ["Greedy"], "target": 2, "minutes": 210, "prerequisites": ["sorting-search"]},
            {"id": "number-theory", "title": "Number theory and combinatorics", "objective": "Use divisibility, modular arithmetic, gcd and counting arguments.", "patterns": ["Number Theory", "Modular Arithmetic", "Math", "Binary Exponentiation"], "topics": ["Number Theory", "Math", "Combinatorics"], "target": 3, "minutes": 240, "prerequisites": ["implementation"]},
            {"id": "bitmasks", "title": "Bit manipulation", "objective": "Apply bitwise identities and reason about fixed-width representations.", "patterns": ["Bit Manipulation", "Bit DP"], "topics": ["Bit Manipulation", "Bitmask"], "target": 2, "minutes": 180, "prerequisites": ["number-theory"]},
            {"id": "contest-practice", "title": "Timed contest practice", "objective": "Practise prioritisation, debugging and post-contest review under a time limit.", "patterns": ["Brute Force", "Constructive Algorithms", "Greedy"], "topics": ["Implementation", "Greedy", "Math"], "target": 3, "minutes": 240, "prerequisites": ["greedy", "number-theory"]},
        ],
    },
]
