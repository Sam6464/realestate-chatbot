import random

urls = [u.strip() for u in open("data/wasalt_product_urls.txt", encoding="utf-8") if u.strip()]
random.seed(42)
sample = random.sample(urls, 150)

with open("data/wasalt_sample_urls.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(sample))

print("Saved", len(sample), "URLs")
print("Three examples to test:")
for u in sample[:3]:
    print(u)