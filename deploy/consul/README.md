---
generated from consul helm template, to make it simple I removed agent Daemonset, pvc, rbac and etc.
```
helm template -n consul --release-name prometheus ./ >consul_template.yaml
````