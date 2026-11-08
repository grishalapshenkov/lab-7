"""
Лабораторная работа № 7. Вариант 14.
Задача А: числа Фибоначчи (наивная рекурсия, мемоизация, итерация), n = 10…32.
Задача Б: размен суммы S = 180, номиналы 1, 5, 12 (ДП, восстановление, сверка с перебором).
Дополнительное задание Г7: отбор проектов в портфель при ограниченном бюджете.
"""
import itertools
import json
import random
import sys
import time

sys.setrecursionlimit(10_000)

calls = 0                       # счётчик вызовов рекурсивной функции


# ------------------------------------------------ задача А: числа Фибоначчи
def fib_naive(n):
    """Наивная рекурсия: Θ(φⁿ) вызовов."""
    global calls
    calls += 1
    if n < 2:
        return n
    return fib_naive(n - 1) + fib_naive(n - 2)


def fib_memo(n, cache=None):
    """Нисходящее ДП (мемоизация): 2n − 1 вызовов."""
    global calls
    calls += 1
    if cache is None:
        cache = {}
    if n < 2:
        return n
    if n in cache:
        return cache[n]
    cache[n] = fib_memo(n - 1, cache) + fib_memo(n - 2, cache)
    return cache[n]


def fib_iter(n):
    """Восходящее ДП: Θ(n) времени, O(1) памяти."""
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def measure(func, n, loops):
    """Среднее время одного вызова (с) и число вызовов рекурсивной функции."""
    global calls
    calls = 0
    result = func(n)
    n_calls = calls
    t0 = time.perf_counter()
    for _ in range(loops):
        func(n)
    return (time.perf_counter() - t0) / loops, n_calls, result


# ------------------------------------------------ задача Б: размен суммы
def change_dp(coins, S):
    """Минимальное число монет. Возвращает (число монет, список монет) или None.
    D[s] = 1 + min D[s − c]; в last[s] запоминается выбранная монета."""
    INF = float("inf")
    D = [0] + [INF] * S
    last = [0] * (S + 1)
    for s in range(1, S + 1):
        for c in coins:
            if c <= s and D[s - c] + 1 < D[s]:
                D[s] = D[s - c] + 1
                last[s] = c
    if D[S] == INF:
        return None
    chosen, s = [], S
    while s > 0:                       # восстановление набора монет
        chosen.append(last[s])
        s -= last[s]
    return D[S], sorted(chosen, reverse=True), D, last


def change_naive(coins, S):
    """Рекурсия без запоминания (для демонстрации перекрывающихся подзадач)."""
    global calls
    calls += 1
    if S == 0:
        return 0
    best = float("inf")
    for c in coins:
        if c <= S:
            best = min(best, 1 + change_naive(coins, S - c))
    return best


def change_brute(coins, S):
    """Полный перебор: числа монет каждого номинала (только для проверки)."""
    best = None
    for counts in itertools.product(*[range(S // c + 1) for c in coins]):
        if sum(k * c for k, c in zip(counts, coins)) == S:
            total = sum(counts)
            if best is None or total < best:
                best = total
    return best


def change_greedy(coins, S):
    """Жадный размен (для сопоставления): всегда наибольший номинал."""
    count = 0
    for c in sorted(coins, reverse=True):
        count += S // c
        S %= c
    return count


# ------------------------------------------- Г7: портфель проектов (рюкзак)
def portfolio_dp(costs, profits, budget):
    """Рюкзак 0/1: возвращает (прибыль, индексы проектов, строка D[N][·] по бюджетам)."""
    n = len(costs)
    D = [[0] * (budget + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        c, p = costs[i - 1], profits[i - 1]
        for b in range(budget + 1):
            D[i][b] = D[i - 1][b]
            if c <= b and D[i - 1][b - c] + p > D[i][b]:
                D[i][b] = D[i - 1][b - c] + p
    return D


def portfolio_restore(D, costs, budget):
    chosen, b = [], budget
    for i in range(len(costs), 0, -1):
        if D[i][b] != D[i - 1][b]:
            chosen.append(i - 1)
            b -= costs[i - 1]
    return sorted(chosen)


def portfolio_brute_curve(costs, profits, budget):
    """Полный перебор подмножеств: лучшая прибыль для каждого бюджета 0…budget."""
    best_by_cost = [0] * (budget + 1)
    for mask in range(1 << len(costs)):
        c = p = 0
        for i in range(len(costs)):
            if mask >> i & 1:
                c += costs[i]
                p += profits[i]
        if c <= budget and p > best_by_cost[c]:
            best_by_cost[c] = p
    curve, cur = [], 0
    for b in range(budget + 1):
        cur = max(cur, best_by_cost[b])
        curve.append(cur)
    return curve


# ---------------------------------------------------------------- графики
def make_plots(res):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fib = res["fib_ext"]
    ns = [r["n"] for r in fib]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.3))
    axes[0].semilogy(ns, [r["calls_naive"] for r in fib], "o-", label="наивная рекурсия")
    axes[0].semilogy(ns, [r["calls_memo"] for r in fib], "s-", label="мемоизация")
    axes[0].set_title("Число вызовов функции")
    axes[1].semilogy(ns, [r["t_naive"] for r in fib], "o-", label="наивная рекурсия")
    axes[1].semilogy(ns, [r["t_memo"] for r in fib], "s-", label="мемоизация")
    axes[1].semilogy(ns, [r["t_iter"] for r in fib], "^-", label="итерация")
    axes[1].axhline(10, color="gray", ls="--", lw=1)
    axes[1].set_title("Время вычисления, с (пунктир — 10 с)")
    for ax in axes:
        ax.set_xlabel("n"); ax.grid(True, which="both", alpha=.3); ax.legend(fontsize=8)
    plt.tight_layout(); plt.savefig("img/lr7_fib.png", dpi=170); plt.close()

    pf = res["portfolio"]
    plt.figure(figsize=(7, 4.3))
    plt.step(range(len(pf["curve"])), pf["curve"], where="post")
    plt.axvline(pf["budget"], color="red", ls="--", lw=1, label=f"бюджет {pf['budget']} млн руб.")
    plt.xlabel("бюджет, млн руб."); plt.ylabel("максимальная прибыль портфеля, млн руб.")
    plt.title("Зависимость прибыли портфеля от бюджета"); plt.grid(True, alpha=.3); plt.legend()
    plt.tight_layout(); plt.savefig("img/lr7_portfolio.png", dpi=170); plt.close()


# ------------------------------------------------------------------- main
if __name__ == "__main__":
    res = {}

    # --- Часть 1. Числа Фибоначчи, n = 10…32
    print(f"{'n':>4} {'наивная, с':>12} {'вызовов':>12} {'мемо, с':>10} {'вызовов':>9} {'итер., с':>10} {'F(n)':>12}")
    res["fib"] = []
    for n in [10, 15, 20, 25, 30, 32]:
        loops_naive = 200 if n <= 20 else (5 if n == 25 else 1)
        t_n, c_n, r1 = measure(fib_naive, n, loops_naive)
        t_m, c_m, r2 = measure(fib_memo, n, 5000)
        t_i, _, r3 = measure(fib_iter, n, 20000)
        assert r1 == r2 == r3
        res["fib"].append({"n": n, "t_naive": t_n, "calls_naive": c_n, "t_memo": t_m,
                           "calls_memo": c_m, "t_iter": t_i, "F": r1})
        print(f"{n:>4} {t_n:>12.4f} {c_n:>12} {t_m:>10.6f} {c_m:>9} {t_i:>10.6f} {r1:>12}", flush=True)

    # --- предельное n для наивной рекурсии (ориентир — 10 с)
    res["fib_ext"] = [dict(r) for r in res["fib"]]
    n = 32
    while True:
        n += 1
        t_n, c_n, r1 = measure(fib_naive, n, 1)
        t_m, c_m, r2 = measure(fib_memo, n, 2000)
        t_i, _, r3 = measure(fib_iter, n, 5000)
        assert r1 == r2 == r3
        res["fib_ext"].append({"n": n, "t_naive": t_n, "calls_naive": c_n, "t_memo": t_m,
                               "calls_memo": c_m, "t_iter": t_i, "F": r1})
        print(f"{n:>4} {t_n:>12.3f} {c_n:>12}", flush=True)
        if t_n > 10:
            res["fib_limit"] = n
            break

    # --- Часть 2. Размен суммы S = 180, номиналы 1, 5, 12
    COINS, S = (1, 5, 12), 180
    count, chosen, D, last = change_dp(COINS, S)
    res["change"] = {"S": S, "coins": COINS, "count": count, "chosen": chosen,
                     "D_head": D[:31], "last_head": last[:31]}
    print(f"\nРазмен S = {S}: {count} монет, набор {chosen}")

    # сверка с полным перебором: все суммы 0…180 для системы варианта и случайные системы
    for s in range(S + 1):
        assert change_dp(COINS, s)[0] == change_brute(COINS, s), s
    rng = random.Random(14)
    for _ in range(100):
        coins = tuple(sorted({1, *rng.sample(range(2, 16), rng.randint(1, 3))}))
        s = rng.randint(1, 40)
        assert change_dp(coins, s)[0] == change_brute(coins, s), (coins, s)
    res["change"]["greedy_fail"] = [s for s in range(1, S + 1)
                                    if change_greedy(COINS, s) != change_dp(COINS, s)[0]]
    print("Проверка с перебором пройдена; жадность ошибается на", len(res["change"]["greedy_fail"]), "суммах")

    # рекурсия без запоминания против ДП
    res["change_naive"] = []
    for s in (10, 20, 30, 40, 50, 60):
        calls = 0
        t0 = time.perf_counter(); v = change_naive(COINS, s); t = time.perf_counter() - t0
        res["change_naive"].append({"S": s, "calls": calls, "t": t, "dp_cells": s * len(COINS)})
        print(f"S = {s}: вызовов {calls}, {t:.4f} с", flush=True)
        if t > 10:
            break

    # --- Г7. Портфель проектов: 12 проектов, затраты и прибыль в млн руб.
    rng = random.Random(14)
    N = 12
    costs = [rng.randint(8, 45) for _ in range(N)]
    profits = [rng.randint(12, 120) for _ in range(N)]
    total = sum(costs)
    D2 = portfolio_dp(costs, profits, total)
    curve = D2[N][:]
    assert curve == portfolio_brute_curve(costs, profits, total), "ДП и перебор расходятся"
    B0 = 100
    items = portfolio_restore(D2, costs, B0)
    res["portfolio"] = {"costs": costs, "profits": profits, "total": total, "curve": curve,
                        "budget": B0, "items": items, "profit": curve[B0],
                        "cost": sum(costs[i] for i in items)}
    print("Портфель при бюджете", B0, ":", items, curve[B0])

    with open("res/lr7.json", "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False)
    make_plots(res)
