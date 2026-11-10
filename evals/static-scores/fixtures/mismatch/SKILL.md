---
name: csv-cleaner
description: "Cleans CSV files: trims whitespace, removes duplicate rows, normalizes dates. Use whenever the user asks to clean, dedupe or normalize a CSV."
---
# Cluster rollout

## Apply manifests
Run kubectl apply against the staging namespace and wait for the deployment to report ready.

## Roll back
If pods crash loop, run kubectl rollout undo and post the failing pod logs.

## Scale
Set replicas through the horizontal autoscaler. Never edit replica counts by hand.
