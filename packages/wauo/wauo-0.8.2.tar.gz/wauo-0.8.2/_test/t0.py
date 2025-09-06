import random

from wauo.spider_tools import gen_random_ua, retry

for i in range(10):
    print(gen_random_ua())


@retry(is_raise=False)
def demo():
    return 1 / 0


class Spider:
    @retry(is_raise=False)
    def crawl(self):
        v = random.randint(1, 2)
        assert v == 2, "~_~"
        return v


if __name__ == '__main__':
    # demo()
    go = Spider().crawl
    print(go())
