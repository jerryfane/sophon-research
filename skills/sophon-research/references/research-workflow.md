# Sophon Research Workflow

Use this file when producing a cited research answer, comparison, or entity map.

## General Pattern

1. Search broadly:

   ```sh
   sophon-research search "<topic>" --limit 5 --json
   ```

2. Choose candidate slugs by relevance, entity type, and source quality.
3. Fetch details:

   ```sh
   sophon-research get <type> <slug> --json
   ```

4. Follow relationships in the JSON: scores, capabilities, publishers,
   organizations, papers, tools, models, and canonical URLs.
5. Verify important technical claims against primary papers, benchmark repos, or
   official model/tool docs before presenting them as facts.

## Eval Or Benchmark Discovery

- Search by benchmark name, task type, capability, or domain.
- Fetch the eval entity and inspect `scores`, `capabilities`, `publisherOrg`,
  `canonicalUrl`, `license`, `format`, and `shortDescription`.
- If comparing scores, preserve each score's wording and conditions. Do not
  normalize benchmark numbers unless the entity states a compatible metric.

## Model Or Tool Comparison

- Search for each model/tool and fetch entities by slug.
- Compare only like-for-like evaluations. Note when scores come from different
  eval versions, subsets, tools, or reporting conditions.
- Include source links from entity fields such as `canonicalUrl`, paper links,
  or organization/project URLs.

## Paper Discovery

- Search by paper title, benchmark, method, author, or capability.
- Fetch the paper entity first. Use paper text/PDF endpoints only when Sophon
  exposes them under the source license.
- Preview text with:

  ```sh
  sophon-research paper <paper-slug> --text
  ```

- Save full text or PDF outside the repo when needed:

  ```sh
  sophon-research paper <paper-slug> --text --output /tmp/paper.txt
  sophon-research paper <paper-slug> --pdf --output /tmp
  ```

## Answer Requirements

- Cite or link sources for claims derived from Sophon data.
- Distinguish direct Sophon fields from your own inference.
- State uncertainty when relationships are weak, indirect, or absent.
- Mention that Sophon is a discovery source when final accuracy requires
  primary-source verification.
- Keep summaries concise unless the user asks for detailed notes.
