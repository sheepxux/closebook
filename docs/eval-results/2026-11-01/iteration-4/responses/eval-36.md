按你选的分节节奏，我们先讲完这三个相关用法，再逐题检查。这次根据通用 Python 知识讲解；用“普通循环对照 + 预测结果”，帮助你把新写法接到已有基础上。

1. 用一行构建新列表

假设要把每个数平方，你熟悉的写法是：

    nums = [2, 3, 4]
    squares = []
    for n in nums:
        squares.append(n * n)

列表推导式把它写成：

    squares = [n * n for n in nums]

理解时先看 for n in nums：依次取出每个数，命名为 n。再看前面的 n * n：计算要放进新列表的值。最外面的方括号把这些值收集成新列表，原来的 nums 不变。

基本形式是：

    [要放入的值 for 元素 in 来源]

2. 用 if 筛选

现在只保留偶数：

    evens = [n for n in nums if n % 2 == 0]

对应的普通循环是：

    evens = []
    for n in nums:
        if n % 2 == 0:
            evens.append(n)

这里 % 是求余数，除以 2 余数为 0 就是偶数。末尾的 if 决定“这个元素是否入选”；最前面的表达式决定“入选后放进去什么”。

所以也可以只对偶数求平方：

    squares = [n * n for n in nums if n % 2 == 0]

先筛选原来的 n，再计算要收集的值。

3. 写入两层循环

假设每种颜色都要搭配每个尺码：

    pairs = []
    for color in ["红", "蓝"]:
        for size in ["S", "M"]:
            pairs.append((color, size))

写成列表推导式：

    pairs = [(color, size) for color in ["红", "蓝"]
             for size in ["S", "M"]]

两个 for 的顺序与普通循环一致：外层在前，内层在后。每取一个 color，都要把所有 size 遍历完，才换下一个 color。前面的 (color, size) 把一次搭配装成一个元组，作为新列表中的一个元素。

现在把讲解移出视线，不往上翻。先检查第一个用法，暂时不运行：

    nums = [1, 4, 6]
    result = [n + 3 for n in nums]

result 的值是什么？请回复“结果 + 一句理由 + 信心 1–3”（1＝猜的，2＝有些把握，3＝很确定）。