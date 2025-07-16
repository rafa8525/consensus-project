# Patch: Partial Restore & Data Reconciliation

## Problem
No instructions for resolving fragmented log/fitness data after recovery.

## Solution
Add to `centralized_knowledge_base.txt`:

> On reconnected sync after interruption:
> - Compare incoming data blocks with existing history
> - Log all partial restores in a system journal with version IDs
> - Broadcast a consistency check request to peer nodes