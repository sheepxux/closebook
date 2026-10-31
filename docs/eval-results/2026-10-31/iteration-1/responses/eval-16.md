Good, that's a tight scope. Since there's no material attached, this outline is my proposal from general HTTP knowledge, so it may not match your course exactly:

1. [core · conceptual] no-cache vs no-store: what each one lets a cache do with a response it received
2. [core · conceptual] max-age: the freshness window, and what happens before vs after it runs out
3. [important · judgment] Picking directives per resource (e.g. an HTML page, a fingerprinted JS bundle, a page showing account data)

Optional extension, not today unless you want it: must-revalidate, private/public, s-maxage, immutable, Expires.

You've studied it before, so I'll skip the teaching and open each point with a question. I'll only explain what your answers show is missing, then retest you closed-book.

One reply is enough:
a) Time today: 15 / 30 / 60 min?
b) Any change to the list? (e.g. "drop 3", "add must-revalidate")

Or just say "go" and I'll use 30 minutes and the list as is.
