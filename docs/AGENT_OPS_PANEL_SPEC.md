# Agent Ops Panel Specification

Agent Ops Panel is a reference interface for operating professional agents.

It should manage:

- agent registry;
- workflow registry;
- task and run records;
- knowledge sources;
- feedback events;
- memory candidates;
- approvals;
- scorecards.

## Scope

The panel is a supplement to the methodology. It should visualize and manage records, but not become the core identity of the project.

## First Version

- Local JSON storage.
- Read-only dashboard.
- Feedback event submission.
- Knowledge source registration.
- Memory candidate review.

## Risk Boundary

No production action should be executed from the panel unless an explicit approval workflow exists.
