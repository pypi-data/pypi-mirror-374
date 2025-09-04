# LIVESEARCH

This is a very simple package

```python
import livesearch

items = [
    "pineapple",
    "banana",
    "apple",
]

results = livesearch.search_strings("app", items)

for res in results:
    print(res.get_obj())
```

This will print:
```
apple
pineapple
```

## Notes

- Regex always enabled

## FAQ

Is this the fastest search
> No

Will this be updated in the future
> If I feel like it, or people start using it a lot
