# EvCode Multi-Assistant Risk Review Requirement

Date: 2026-03-18

## Goal

Stress-test the proposed EvCode multi-assistant routing design from the opposite direction and identify the structural risks, failure modes, and reasons the design could fail in practice.

## Deliverables

- a risk review of the multi-assistant architecture
- clear identification of fatal, high, medium, and low risks
- judgment on whether the design should proceed, be narrowed, or be restructured
- mitigation guidance for the risks that are worth accepting

## Constraints

- preserve the existing governed-runtime truth as the baseline for critique
- evaluate the design against EvCode's current architecture rather than as a greenfield system
- do not hide risks behind vague optimism
- distinguish between desirable ambition and operationally safe scope

## Acceptance Criteria

- the critique identifies concrete failure modes rather than generic concerns
- the critique explains why each risk matters specifically for EvCode
- the critique distinguishes “fixable with controls” from “design-breaking” risks
- the critique ends with a go / narrow / no-go judgment

## Non-Goals

- implementing mitigations in this turn
- proving external assistants are available or production-ready on this machine
- rewriting the previously proposed multi-assistant architecture
