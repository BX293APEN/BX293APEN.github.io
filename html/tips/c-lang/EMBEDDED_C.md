# 組み込み C 実践メモ — 一般編 + RP2040 (Raspberry Pi Pico W) 編

---

## 目次

1. [整数型と符号なし整数のオーバーフロー](#整数型と符号なし整数のオーバーフロー)
2. [整数リテラルのサフィックス — `U` `L` `UL` `ULL`](#整数リテラルのサフィックス--u-l-ul-ull)
3. [定数定義 — `#define` と `enum`](#定数定義--define-と-enum)
4. [プリプロセッサ / マクロ](#プリプロセッサ--マクロ)
5. [可変引数関数 — `va_list` / `vsnprintf` の仕組み](#可変引数関数--va_list--vsnprintf-の仕組み)
6. [時刻構造体と整形出力 — `struct tm` / `strftime`](#時刻構造体と整形出力--struct-tm--strftime)
7. [構造体 — 定義・初期化・アクセス](#構造体--定義初期化アクセス)
8. [関数ポインタ](#関数ポインタ)
9. [`const` / `static` / `static const` — 修飾子の組み合わせと保存先](#const--static--static-const--修飾子の組み合わせと保存先)
10. [`volatile` — 最適化を止める](#volatile--最適化を止める)
11. [`__attribute__` と `weak` 属性](#__attribute__-と-weak-属性)
12. [3 つのメモリ領域 — スタック / ヒープ / 静的領域](#3-つのメモリ領域--スタック--ヒープ--静的領域)
13. [ブロックスコープ `{}` と変数の寿命](#ブロックスコープ--と変数の寿命)
14. [`-O2` / `-Os` 最適化 — 何が消えて何が残るか](#-o2---os-最適化--何が消えて何が残るか)
15. [メモリ削減テクニック まとめ](#メモリ削減テクニック-まとめ)
16. [RP2040 固有 — セクションとメモリの対応](#rp2040-固有--セクションとメモリの対応)
17. [RP2040 固有 — `const` グローバル変数がフラッシュに置かれる理由](#rp2040-固有--const-グローバル変数がフラッシュに置かれる理由)
18. [RP2040 固有 — `__attribute__((aligned(4)))` の意味](#rp2040-固有--__attribute__aligned4-の意味)

---

## 整数型と符号なし整数のオーバーフロー

### 標準整数型のバイト数とビット幅

C の基本型はプラットフォームによってサイズが変わるため、
組み込みでは `<stdint.h>` の固定幅型を使うのが鉄則。

```c
#include <stdint.h>

// 符号なし整数 (unsigned)
uint8_t   u8;   // 1 バイト  0 〜 255
uint16_t  u16;  // 2 バイト  0 〜 65,535
uint32_t  u32;  // 4 バイト  0 〜 4,294,967,295
uint64_t  u64;  // 8 バイト  0 〜 18,446,744,073,709,551,615

// 符号あり整数 (signed)
int8_t    s8;   // 1 バイト  -128 〜 127
int16_t   s16;  // 2 バイト  -32,768 〜 32,767
int32_t   s32;  // 4 バイト  -2,147,483,648 〜 2,147,483,647
int64_t   s64;  // 8 バイト  -9.2 × 10^18 〜 9.2 × 10^18

// 最大値・最小値マクロ (<stdint.h> に定義済み)
// UINT8_MAX = 255,  INT8_MIN = -128,  INT8_MAX = 127  ... など
```

### 符号なし整数のラップアラウンド (正式仕様)

C 規格では符号なし整数のオーバーフローは **未定義動作ではなく**、
`2^N` を法とする剰余演算 (モジュロ) と規定されている。

```c
uint8_t x = 255;
x++;          // 256 % 256 = 0 → x == 0 (0 に戻る)

uint8_t y = 0;
y--;          // -1 % 256 = 255 → y == 255 (最大値に折り返す)

uint16_t z = 65535;
z++;          // 0 に戻る
```

```
uint8_t のラップアラウンドイメージ

  254 → 255 → [0] → 1 → 2 ...
               ↑
             ここでラップ
```

### 符号あり整数のオーバーフローは未定義動作

```c
int8_t a = 127;
a++;   // ❌ 未定義動作 (UB) — コンパイラが何をしても良い
       // 実際には -128 になることが多いが保証されない

// ✅ 符号ありでカウンタが必要なら範囲チェックを入れる
if (a < INT8_MAX) a++;
```

### 型変換の落とし穴

```c
uint8_t  a = 200;
uint8_t  b = 100;
uint8_t  result = a + b;   // ❌ 300 → 44 (オーバーフロー)
uint16_t result2 = (uint16_t)a + b;  // ✅ 300 (キャストして拡張)

// 比較での符号ミスマッチ
int32_t  len = -1;
uint32_t size = 10;
if (len < size) { ... }   // ❌ -1 が巨大な正数に変換されて条件が偽になる
                          //    符号なしと符号ありの比較は要注意
```

---

## 整数リテラルのサフィックス — `U` `L` `UL` `ULL`

数値リテラルに何もつけないと `int` (符号あり 32 bit) 扱いになる。
大きな値・符号なし・64 bit が必要なときはサフィックスで型を明示する。

### サフィックス一覧

| サフィックス | 型 | バイト | 例 |
|---|---|---|---|
| なし | `int` | 4 | `1000` |
| `U` / `u` | `unsigned int` | 4 | `1000U` |
| `L` / `l` | `long` (環境依存) | 4 or 8 | `1000L` |
| `UL` / `ul` | `unsigned long` | 4 or 8 | `1000UL` |
| `LL` / `ll` | `long long` | 8 | `1000LL` |
| `ULL` / `ull` | `unsigned long long` | 8 | `1000ULL` |
| `f` / `F` | `float` | 4 | `3.14f` |
| (なし) | `double` | 8 | `3.14` |

> **`long` は環境依存**: Windows 64 bit では 4 バイト、Linux 64 bit では 8 バイト。
> 組み込みでは `long` を避けて `int32_t` / `uint32_t` を使うのが安全。

### なぜサフィックスが必要か

```c
// ① オーバーフロー防止
uint32_t ms = 60 * 1000;       // ❌ 60 と 1000 は int → 計算も int で行われる
                                //    int の範囲内なら OK だがギリギリ
uint32_t ms = 60 * 1000U;      // ✅ 1000U で unsigned に昇格して計算される
uint32_t big = 3000 * 1000;    // ❌ 3,000,000 は int 範囲内だが…
uint32_t big = 3000UL * 1000;  // ✅ 明示的に unsigned long で計算

// ② タイムアウト・周波数など大きな値の #define
#define TIMEOUT_MS    60000U        // U をつけて unsigned に
#define CPU_FREQ_HZ   125000000UL   // 125 MHz — UL で unsigned long
#define MAX_SIZE      0xFFFFFFFFU   // 32 bit 全ビット 1 — U 必須

// ③ ビットシフトで 64 bit が必要なとき
uint64_t mask = 1ULL << 32;    // ✅ 1ULL で 64 bit にしてからシフト
uint64_t mask2 = 1 << 32;      // ❌ 1 は 32 bit int → シフト結果が 0 になる (UB)
```

### サフィックスなしで起きるバグの例

```c
// よくある罠: int 同士の演算結果が int に収まらない
uint32_t timeout = 24 * 60 * 60 * 1000;   // 86,400,000 ms (1日)
// 24 * 60 * 60 * 1000 = 86,400,000
// int の最大値は 2,147,483,647 なので範囲内… だがギリギリ
// → 掛け算の途中で int を超えると UB になる環境もある

uint32_t timeout2 = 24UL * 60 * 60 * 1000;  // ✅ 最初の項を UL にすれば安全

// float / double の混在
float f = 1.0 / 3.0;    // 1.0 と 3.0 は double → double 演算 → float に代入で精度落ち
float f2 = 1.0f / 3.0f; // ✅ float のまま計算 (組み込みでは float が速いことが多い)
```

---

## 定数定義 — `#define` と `enum`

### `#define` による定数

```c
// 数値定数
#define MAX_RETRY    3
#define TIMEOUT_MS   1000
#define PI_APPROX    3.14159f    // f サフィックスで float リテラル

// 文字列定数
#define VERSION_STR  "1.0.0"

// ビットマスク (16進数)
#define FLAG_READY   0x01
#define FLAG_BUSY    0x02
#define FLAG_ERROR   0x04
#define ALL_FLAGS    (FLAG_READY | FLAG_BUSY | FLAG_ERROR)
```

`#define` はプリプロセッサによる**テキスト置換**であり、型を持たない。
デバッガで値が見えないことがあるため、型が必要な場合は `enum` や `const` を使う。

### `enum` による列挙定数

```c
// デフォルト: 0 から 1 ずつ増加
typedef enum {
    STATE_IDLE = 0,
    STATE_CONNECTING,    // 1
    STATE_CONNECTED,     // 2
    STATE_ERROR,         // 3
} wifi_state_t;

// 途中から値を指定することもできる
typedef enum {
    LOG_NONE  = 0,
    LOG_ERROR = 1,
    LOG_WARN  = 2,
    LOG_INFO  = 4,
    LOG_DEBUG = 8,
} log_level_t;

// 使い方
wifi_state_t state = STATE_IDLE;
if (state == STATE_CONNECTED) { ... }
```

### `#define` vs `enum` の使い分け

| | `#define` | `enum` |
|---|---|---|
| 型 | なし (テキスト置換) | `int` (コンパイラが管理) |
| デバッガ表示 | 値のみ | 名前が見える場合あり |
| スコープ | グローバル (ファイル全体) | 通常はグローバル |
| 使い所 | ビットマスク・文字列・マクロ展開 | 状態機械・モード列挙 |
| 連番自動付与 | ❌ | ✅ |

---

## プリプロセッサ / マクロ

C プリプロセッサはコンパイル前にソースをテキスト変換する。
組み込みではビルド設定の切り替え・ポータビリティ確保に多用される。

### 基本的なディレクティブ

```c
// ── 定義と条件分岐 ──────────────────────────────────
#define DEBUG_LEVEL 2        // マクロ定義
#undef  DEBUG_LEVEL          // 定義を削除

#ifdef  DEBUG_LEVEL          // 定義されているなら
#ifndef RELEASE              // 定義されていないなら
#if     DEBUG_LEVEL >= 2     // 値で比較
#elif   DEBUG_LEVEL == 1     // else if
#else                        // それ以外
#endif                       // 条件ブロック終端

// ── ファイルインクルード ─────────────────────────────
#include <stdio.h>           // システムヘッダ (インクルードパスを検索)
#include "my_module.h"       // ローカルヘッダ (カレントディレクトリ優先)

// ── インクルードガード (ヘッダの多重インクルード防止) ─
#ifndef MY_MODULE_H
#define MY_MODULE_H
// ... ヘッダ内容 ...
#endif
```

### `#if` で使える演算子

```c
#define VER_MAJOR 1
#define VER_MINOR 2
#define FEATURE_X        // 値なしで "定義されている" という意味にも使える

// 算術・比較演算子
#if VER_MAJOR > 1
#if VER_MINOR >= 2
#if (VER_MAJOR * 100 + VER_MINOR) >= 102

// 論理演算子
#if defined(FEATURE_X) && (VER_MAJOR >= 1)   // &&  AND
#if defined(FEATURE_X) || defined(FEATURE_Y)  // ||  OR
#if !defined(RELEASE)                          // !   NOT

// defined() 演算子 — ifdef の式版 (&&/|| と組み合わせるとき必須)
#if defined(FEATURE_X) && defined(FEATURE_Y)  // ✅ 両方定義されているとき
// #ifdef FEATURE_X && FEATURE_Y  ← ❌ ifdef は && と組み合わせられない
```

### 関数マクロ

```c
// 単純な式マクロ — 引数は必ずカッコで囲む
#define MAX(a, b)      ((a) > (b) ? (a) : (b))
#define MIN(a, b)      ((a) < (b) ? (a) : (b))
#define ABS(x)         ((x) < 0 ? -(x) : (x))
#define BIT(n)         (1u << (n))             // n ビット目を立てる
#define ARRAY_SIZE(a)  (sizeof(a) / sizeof((a)[0]))  // 配列の要素数

// ❌ カッコなしは演算子優先度バグの原因
#define BAD_DOUBLE(x)  x * 2        // BAD_DOUBLE(1+1) → 1+1*2 = 3 (期待値は 4)
#define GOOD_DOUBLE(x) ((x) * 2)    // GOOD_DOUBLE(1+1) → (1+1)*2 = 4
```

### 複数文マクロ — `do { } while(0)` イディオム

```c
// ❌ 複数文をそのまま書くと if-else で壊れる
#define BAD_LOG(x)   printf("val=%d\n", x); log_write(x)
// if (cond) BAD_LOG(v);
// → if (cond) printf(...);  log_write(v);  ← log_write は常に実行される

// ✅ do-while(0) で 1 文として扱う
#define LOG(x) \
    do { \
        printf("val=%d\n", (x)); \
        log_write((x)); \
    } while (0)
// if (cond) LOG(v);  → do { ... } while(0) が 1 文として扱われ正しく動く
```

### 可変引数マクロ と `##__VA_ARGS__`

```c
// __VA_ARGS__ で printf スタイルのデバッグログ
#ifdef DEBUG
  #define DBG(fmt, ...)    printf("[DBG] " fmt "\n", ##__VA_ARGS__)
#else
  #define DBG(fmt, ...)    ((void)0)  // リリースビルドで完全消去
#endif

DBG("x=%d, y=%d", x, y);   // → [DBG] x=3, y=5
DBG("hello");               // 引数なし — ## が余分なカンマを消す

// __FILE__, __LINE__, __func__ で位置情報を付加
#define ERR(fmt, ...) \
    printf("[ERR %s:%d] " fmt "\n", __FILE__, __LINE__, ##__VA_ARGS__)
```

### 文字列化 `#` と トークン連結 `##`

```c
// # — 引数をそのまま文字列リテラルにする
#define STRINGIFY(x)  #x
STRINGIFY(hello)   // → "hello"
STRINGIFY(1 + 2)   // → "1 + 2"

// ## — トークンを連結する
#define MAKE_VAR(prefix, n)  prefix##n
int MAKE_VAR(buf, 1) = 0;   // → int buf1 = 0;
int MAKE_VAR(buf, 2) = 0;   // → int buf2 = 0;
```

### ビルド済み定義済みマクロ

```c
printf("%s\n", __FILE__);    // "main.c"  (ファイル名)
printf("%d\n", __LINE__);    // 42        (行番号)
printf("%s\n", __func__);    // "main"    (関数名, C99以降)
printf("%s\n", __DATE__);    // "Jun  4 2026"
printf("%s\n", __TIME__);    // "12:34:56"
```

---

## 可変引数関数 — `va_list` / `vsnprintf` の仕組み

`printf` のように引数の個数・型が呼び出しごとに変わる関数を**可変引数関数**という。
`<stdarg.h>` が提供する 4 つのマクロで実装する。

### 基本的な仕組み — `<stdarg.h>` の 4 マクロ

```c
#include <stdarg.h>

// va_list   — 可変引数の「現在位置」を保持する型 (ポインタのようなもの)
// va_start  — va_list を初期化。最後の固定引数名を渡す
// va_arg    — 次の引数を指定型で取り出す (取り出すたびに位置が進む)
// va_end    — va_list の後始末 (必ず呼ぶ)

void my_print(const char *fmt, ...) {  // ... が可変引数部分
    va_list ap;
    va_start(ap, fmt);   // fmt の次から可変引数が始まる

    // ここで ap を使って引数を取り出す ...

    va_end(ap);          // 後始末 — 忘れると未定義動作
}
```

```
スタック上のイメージ (呼び出し時)

  my_print("x=%d y=%d", 10, 20) の場合

  │  20        │  ← va_arg 2 回目で取り出す
  │  10        │  ← va_arg 1 回目で取り出す
  │ "x=%d y=%d"│  ← fmt (最後の固定引数)
  │ 戻りアドレス│
  └────────────┘
    va_start(ap, fmt) で ap が fmt の直後を指す
```

### `va_arg` で引数を 1 つずつ取り出す

```c
#include <stdio.h>
#include <stdarg.h>

// 整数を n 個受け取って合計を返す
int sum_ints(int count, ...) {
    va_list ap;
    va_start(ap, count);   // count が最後の固定引数

    int total = 0;
    for (int i = 0; i < count; i++) {
        total += va_arg(ap, int);  // int として 1 つ取り出す
    }

    va_end(ap);
    return total;
}

// 使い方
int s = sum_ints(3, 10, 20, 30);  // → 60
```

> **`va_arg` の型指定は呼び出し側と一致させる**こと。
> `va_arg(ap, int)` なのに `float` を渡すと**未定義動作**。
> `float` は `double` に昇格されてスタックに積まれるため `va_arg(ap, double)` が正しい。

### `va_copy` — `va_list` のコピー

```c
// ap を 2 回走査したいとき (1 回目でサイズ計測、2 回目で書き込みなど)
va_list ap, ap2;
va_start(ap, fmt);
va_copy(ap2, ap);   // ap の現在位置をコピー

// ap で 1 回目の走査
// ap2 で 2 回目の走査 (最初から)

va_end(ap2);        // コピーにも va_end が必要
va_end(ap);
```

---

### `v` 系関数 — `va_list` をそのまま渡せる printf 族

`printf` / `sprintf` / `snprintf` には `va_list` を受け取る兄弟関数がある。
自分で可変引数ラッパーを作るとき必ず使う。

| 通常版 | `va_list` 版 | 主な用途 |
|--------|-------------|---------|
| `printf` | `vprintf` | 標準出力に書式出力 |
| `sprintf` | `vsprintf` | 文字列バッファに書式出力 (バッファ長チェックなし ⚠️) |
| `snprintf` | `vsnprintf` | バッファ長を指定して安全に書式出力 ✅ |
| `fprintf` | `vfprintf` | ファイルに書式出力 |

```c
// 組み込み・一般 C 共通の安全なラッパー実装パターン
#include <stdio.h>
#include <stdarg.h>

void my_log(const char *fmt, ...) {
    char buf[128];
    va_list ap;
    va_start(ap, fmt);

    // vsnprintf — バッファサイズを渡して安全に書式化
    // 戻り値: 書き込もうとした文字数 (終端 \0 除く)
    //         >= size なら切り捨てが起きている
    int n = vsnprintf(buf, sizeof(buf), fmt, ap);

    va_end(ap);

    if (n >= (int)sizeof(buf)) {
        // 切り捨て発生 — 必要なら対処
    }
    uart_puts(buf);  // 実際の出力
}
```

### `vsnprintf` の引数と戻り値の詳細

```c
int vsnprintf(char *buf, size_t size, const char *fmt, va_list ap);
//            ↑書き込み先  ↑バッファサイズ  ↑書式文字列  ↑va_list

// ポイント:
// - 最大 size-1 文字を書き込み、末尾に必ず '\0' を付ける
// - 戻り値は「切り捨てなしなら何文字書き込まれるか」(C99 規定)
//   → 戻り値 >= size なら切り捨てが起きている

char buf[16];
int n = vsnprintf(buf, sizeof(buf), "Hello %s!", "World");
// n == 12 ("Hello World!" は 12 文字), buf == "Hello World!"

n = vsnprintf(buf, sizeof(buf), "%d items in stock", 9999999);
// n == 22 (22 文字必要), buf == "9999999 items i" (15 文字 + \0 で切り捨て)
// n >= 16 で切り捨てを検出できる
```

### Windows 固有 — `_vsnprintf_s` と `_TRUNCATE`

Windows (MSVC) では C11 Annex K の「セキュア版」関数が使える。
`_vsnprintf_s` はバッファオーバーランを検出してハンドラを呼ぶ。

```c
// MSVC / Windows SDK のみ。組み込み (GCC/Clang) では使えない
#include <stdio.h>
#include <stdarg.h>

void win_log(const char *fmt, ...) {
    char buf[128];
    va_list ap;
    va_start(ap, fmt);

    // _vsnprintf_s(バッファ, バッファサイズ, 書き込み最大文字数, 書式, va_list)
    //   第3引数に _TRUNCATE を渡すと: 切り捨ててでも書き込む (vsnprintf 互換動作)
    //   第3引数に実サイズを渡すと:   超えたら invalid parameter handler を呼ぶ
    _vsnprintf_s(buf, sizeof(buf), _TRUNCATE, fmt, ap);

    va_end(ap);
    OutputDebugStringA(buf);
}
```

```
_TRUNCATE の意味:
  切り捨てが起きても abort せず、buf に入る分だけ書いて '\0' を保証する。
  組み込みの vsnprintf と同等の "切り捨て許容" 動作になる。
```

> **組み込み (pico-sdk / GCC) では `_vsnprintf_s` は使えない**。
> `vsnprintf` を使う。`_s` 系は MSVC 拡張。

### 移植性のある書き方 — プラットフォーム分岐

```c
#include <stdio.h>
#include <stdarg.h>

static int safe_vsnprintf(char *buf, size_t size, const char *fmt, va_list ap) {
#if defined(_MSC_VER)
    // Windows MSVC
    return _vsnprintf_s(buf, size, _TRUNCATE, fmt, ap);
#else
    // GCC / Clang / pico-sdk
    return vsnprintf(buf, size, fmt, ap);
#endif
}

// これをラップしてどこでも同じように呼ぶ
void log_write(const char *fmt, ...) {
    char buf[256];
    va_list ap;
    va_start(ap, fmt);
    safe_vsnprintf(buf, sizeof(buf), fmt, ap);
    va_end(ap);
    // ... 出力処理 ...
}
```

### `va_list` を再利用するときの注意

```c
// ❌ va_start 後に va_list を 2 回渡してはいけない
void bad(const char *fmt, ...) {
    va_list ap;
    va_start(ap, fmt);
    vsnprintf(buf1, sizeof(buf1), fmt, ap);  // ap の位置が末尾まで進む
    vsnprintf(buf2, sizeof(buf2), fmt, ap);  // ❌ ap はもう終端 → 未定義動作
    va_end(ap);
}

// ✅ 2 回使うなら va_copy でコピーを作る
void good(const char *fmt, ...) {
    va_list ap, ap2;
    va_start(ap, fmt);
    va_copy(ap2, ap);                        // コピー

    vsnprintf(buf1, sizeof(buf1), fmt, ap);  // ap を消費
    vsnprintf(buf2, sizeof(buf2), fmt, ap2); // ap2 (コピー) を消費

    va_end(ap2);
    va_end(ap);
}
```

---

## 時刻構造体と整形出力 — `struct tm` / `strftime`

### `struct tm` — 時刻を人間向けに分解した構造体

`<time.h>` で定義される。年・月・日・時・分・秒をそれぞれのフィールドに持つ。

```c
#include <time.h>

struct tm {
    int tm_sec;    // 秒          [0, 60]  (60 はうるう秒)
    int tm_min;    // 分          [0, 59]
    int tm_hour;   // 時          [0, 23]
    int tm_mday;   // 日 (月内)   [1, 31]
    int tm_mon;    // 月          [0, 11]  ← 0 始まり注意！ (1月=0, 12月=11)
    int tm_year;   // 年          1900 からの差分 ← 注意！ (2024年 → 124)
    int tm_wday;   // 曜日        [0, 6]   (0=日曜)
    int tm_yday;   // 年内通算日  [0, 365]
    int tm_isdst;  // 夏時間フラグ (1=夏時間, 0=通常, -1=不明)
};
```

> **よくある罠**
> - `tm_mon` は **0 始まり** (`0`=1月, `11`=12月)
> - `tm_year` は **1900 年からの差分** (2024年 → `124`)
> - 画面表示するときは `tm_mon + 1`、`tm_year + 1900` に変換する

### `time_t` — Unix エポックからの秒数

```c
time_t now = time(NULL);   // 現在時刻を Unix タイム (1970-01-01 00:00:00 UTC からの秒) で取得
                           // 組み込みでは RTC やネットワーク時刻から設定することが多い
```

### `time_t` ↔ `struct tm` の変換

```c
time_t now = time(NULL);

// ① time_t → struct tm (ローカル時刻)
struct tm *local = localtime(&now);   // 静的バッファを返す (スレッド unsafe)

// ② time_t → struct tm (UTC)
struct tm *utc = gmtime(&now);        // UTC で返す

// ③ struct tm → time_t (逆変換)
struct tm t = { .tm_year = 124, .tm_mon = 5, .tm_mday = 4,
                .tm_hour = 12,  .tm_min = 0, .tm_sec  = 0 };
time_t epoch = mktime(&t);            // ローカル時刻として解釈して変換
```

> `localtime` / `gmtime` は内部の静的バッファへのポインタを返すため、
> 次の呼び出しで上書きされる。保存が必要なら `localtime_r` (POSIX) を使う。

### `strftime` — `struct tm` をバッファに書式化

```c
#include <time.h>

// strftime(書き込み先バッファ, バッファサイズ, 書式文字列, struct tm へのポインタ)
// 戻り値: 書き込んだ文字数 (終端 '\0' 除く)。失敗したら 0

char buf[64];
struct tm *t = localtime(&now);

strftime(buf, sizeof(buf), "%Y-%m-%d %H:%M:%S", t);
// → "2024-06-04 15:30:00"

strftime(buf, sizeof(buf), "%Y/%m/%d", t);
// → "2024/06/04"

strftime(buf, sizeof(buf), "%H:%M", t);
// → "15:30"
```

### よく使う書式指定子

| 指定子 | 内容 | 例 |
|--------|------|----|
| `%Y` | 4 桁年 | `2024` |
| `%y` | 下 2 桁年 | `24` |
| `%m` | 月 (01〜12) | `06` |
| `%d` | 日 (01〜31) | `04` |
| `%H` | 時 24h (00〜23) | `15` |
| `%I` | 時 12h (01〜12) | `03` |
| `%M` | 分 (00〜59) | `30` |
| `%S` | 秒 (00〜60) | `00` |
| `%A` | 曜日フル | `Tuesday` |
| `%a` | 曜日短縮 | `Tue` |
| `%B` | 月名フル | `June` |
| `%b` | 月名短縮 | `Jun` |
| `%p` | AM / PM | `PM` |
| `%j` | 年内通算日 (001〜366) | `156` |
| `%%` | `%` 文字そのもの | `%` |

### 手動で `struct tm` を組み立てて使う

```c
// RTC から読んだ値を直接 struct tm に入れるパターン (組み込みでよくある)
struct tm rtc_time = {
    .tm_year = 2024 - 1900,  // 1900 引く！
    .tm_mon  = 6 - 1,        // 1 引く！ (6月 → 5)
    .tm_mday = 4,
    .tm_hour = 15,
    .tm_min  = 30,
    .tm_sec  = 0,
    .tm_isdst = -1,           // 夏時間不明
};

char buf[32];
strftime(buf, sizeof(buf), "%Y/%m/%d %H:%M:%S", &rtc_time);
// → "2024/06/04 15:30:00"

// 表示するだけなら sprintf でも可 (strftime の方が移植性が高い)
sprintf(buf, "%04d/%02d/%02d %02d:%02d:%02d",
        rtc_time.tm_year + 1900,
        rtc_time.tm_mon  + 1,    // 0 始まりを戻す
        rtc_time.tm_mday,
        rtc_time.tm_hour,
        rtc_time.tm_min,
        rtc_time.tm_sec);
```

### 経過時間の計算

```c
time_t start = time(NULL);
// ... 処理 ...
time_t end = time(NULL);

double elapsed_sec = difftime(end, start);  // 秒単位の差 (double)

// 分・秒に分解
int total_sec = (int)elapsed_sec;
int min = total_sec / 60;
int sec = total_sec % 60;
printf("経過: %d分 %d秒\n", min, sec);
```

---

## 構造体 — 定義・初期化・アクセス

### 基本定義と `typedef`

```c
// typedef なし — 使うたびに struct が必要
struct Point { int x; int y; };
struct Point p;   // struct が必要

// typedef あり — 型名だけで使える (組み込みでよく使うスタイル)
typedef struct {
    int x;
    int y;
} point_t;
point_t p;        // struct 不要
```

### 指示子初期化 (Designated Initializer)

C99 以降で使える。**フィールド名を明示して初期化する方法**で、
順番を気にしなくて良いうえ、未指定フィールドは自動的に 0 になる。

```c
typedef struct {
    const char *server;
    uint16_t    port;
    const char *ssid;
    const char *password;
    const char *local_ip;
    const char *netmask;
    const char *gateway;
    uint16_t    local_port;
} wifi_config_t;

// ✅ 指示子初期化 — フィールド名で指定するので順番変更に強い
static const wifi_config_t g_wifi_configs[] = {
    {
        .server     = "192.168.10.64",
        .port       = 19080,
        .ssid       = "YOUR_SSID",
        .password   = "YOUR_PASSWORD",
        .local_ip   = "192.168.5.10",
        .netmask    = "",            // 空文字で「未設定」を表現
        .gateway    = "",
        .local_port = 8081,
    },
    // 要素を追加するときも .フィールド名 形式で書き足すだけ
};

// 未指定フィールドはゼロ初期化される
static wifi_config_t cfg = { .port = 80 };
// → ssid, password などは NULL (ポインタ), 0 (数値) になる
```

### フィールドアクセス — `.` と `->`

```c
// ① 値 (実体) の場合 → ドット演算子 .
wifi_config_t cfg = { .port = 80 };
uint16_t p = cfg.port;    // 値でアクセス
cfg.port = 443;

// ② ポインタの場合 → アロー演算子 ->
wifi_config_t *ptr = &cfg;
uint16_t p2 = ptr->port;  // ポインタ経由でアクセス
ptr->port = 8080;

// -> は (*ptr).port の糖衣構文
uint16_t p3 = (*ptr).port;  // 同じ意味 (読みにくいので -> を使う)

// 配列の場合
static const wifi_config_t configs[2] = { {...}, {...} };
uint16_t first_port  = configs[0].port;       // 配列要素 (値) → .
uint16_t second_port = (configs + 1)->port;   // ポインタ演算 → ->
```

### 構造体の入れ子

```c
typedef struct {
    float x, y, z;
} vec3_t;

typedef struct {
    vec3_t  position;     // 入れ子構造体
    vec3_t  velocity;
    float   mass;
} body_t;

body_t b = {
    .position = { .x = 1.0f, .y = 0.0f, .z = 0.0f },
    .velocity = { .x = 0.0f, .y = 1.0f, .z = 0.0f },
    .mass     = 10.0f,
};
float px = b.position.x;   // チェーンしてアクセス
```

### `__attribute__((packed))` — パディング除去

```c
// 通常はアライメントのためパディングが挿入される
typedef struct {
    uint8_t  a;     // 1 バイト
    // [3 バイトパディング]
    uint32_t b;     // 4 バイト
} normal_t;         // sizeof = 8

// packed: パディングなし (通信プロトコルのパケット定義に使う)
typedef struct __attribute__((packed)) {
    uint8_t  a;     // 1 バイト
    uint32_t b;     // 4 バイト (1 バイト境界に配置される)
} packed_t;         // sizeof = 5
// ⚠️ 非アライメントアクセスは一部 CPU で遅い・クラッシュする可能性あり
```

---

## 関数ポインタ

関数のアドレスを保持する変数。コールバック・ディスパッチテーブルに使う。

### 基本的な宣言と使い方

```c
// 関数ポインタ型の宣言: 戻り値型 (*変数名)(引数型, ...)
int (*fp)(int, int);    // int を 2 つ受け取り int を返す関数へのポインタ

int add(int a, int b) { return a + b; }
int mul(int a, int b) { return a * b; }

fp = add;              // 関数名 = 関数のアドレス (&add と同じ)
int result = fp(3, 4); // → 7  (ポインタ経由で add を呼び出す)
fp = mul;
result = fp(3, 4);     // → 12

// typedef で読みやすくする (推奨)
typedef int (*math_op_t)(int, int);
math_op_t op = add;
op(2, 3);              // → 5
```

### 関数に関数ポインタを引数として渡す (コールバック)

```c
// コールバックを受け取る関数
void apply_to_array(int *arr, int len, void (*callback)(int *elem)) {
    for (int i = 0; i < len; i++) {
        callback(&arr[i]);   // 引数の関数ポインタを呼び出す
    }
}

// コールバック関数の実装
void double_value(int *elem) { *elem *= 2; }
void clamp_to_100(int *elem) { if (*elem > 100) *elem = 100; }

// 使い方
int data[4] = {10, 20, 30, 40};
apply_to_array(data, 4, double_value);    // 各要素を 2 倍
apply_to_array(data, 4, clamp_to_100);   // 各要素を 100 にクランプ
```

### typedef を使ったより実践的な例

```c
// イベントハンドラの型定義
typedef void (*event_handler_t)(uint8_t event_id, void *user_data);

// ハンドラを登録して呼び出す仕組み
typedef struct {
    event_handler_t handler;
    void           *user_data;
} event_listener_t;

static event_listener_t g_listener;

void event_register(event_handler_t handler, void *user_data) {
    g_listener.handler   = handler;
    g_listener.user_data = user_data;
}

void event_fire(uint8_t id) {
    if (g_listener.handler != NULL) {          // NULL チェック必須
        g_listener.handler(id, g_listener.user_data);  // 呼び出し
    }
}

// 登録側
void my_handler(uint8_t id, void *data) {
    printf("event %d\n", id);
}
event_register(my_handler, NULL);
```

### ディスパッチテーブル (関数ポインタ配列)

```c
// コマンド番号 → 処理関数 のテーブル
typedef void (*cmd_handler_t)(void);

void cmd_start(void) { /* ... */ }
void cmd_stop(void)  { /* ... */ }
void cmd_reset(void) { /* ... */ }

static const cmd_handler_t dispatch_table[] = {
    [0] = cmd_start,   // コマンド 0 → cmd_start
    [1] = cmd_stop,    // コマンド 1 → cmd_stop
    [2] = cmd_reset,   // コマンド 2 → cmd_reset
};
#define CMD_COUNT  ARRAY_SIZE(dispatch_table)

void handle_command(uint8_t cmd) {
    if (cmd < CMD_COUNT && dispatch_table[cmd] != NULL) {
        dispatch_table[cmd]();   // テーブルから引いて呼ぶ
    }
}
```

---

## `const` / `static` / `static const` — 修飾子の組み合わせと保存先

### 一覧表

修飾子の有無によって「どこに保存されるか」「誰から見えるか」「寿命」が決まる。

| 書き方 | 場所 | セクション | 寿命 | 他ファイルから見える？ | 書き換え可？ |
|--------|------|-----------|------|-----------------------|-------------|
| `int x;` (グローバル) | SRAM | `.bss` | プログラム終了まで | ✅ 見える (`extern` で) | ✅ |
| `int x = 1;` (グローバル) | SRAM | `.data` | プログラム終了まで | ✅ 見える | ✅ |
| `static int x;` (グローバル) | SRAM | `.bss` | プログラム終了まで | ❌ このファイルのみ | ✅ |
| `const int x = 1;` (グローバル) | Flash | `.rodata` | プログラム終了まで | ✅ 見える | ❌ |
| `static const int x = 1;` (グローバル) | Flash | `.rodata` | プログラム終了まで | ❌ このファイルのみ | ❌ |
| `int x;` (ローカル) | スタック | — | 関数を抜けるまで | ❌ | ✅ |
| `static int x;` (ローカル) | SRAM | `.bss`/`.data` | プログラム終了まで | ❌ | ✅ |
| `const int x = 1;` (ローカル) | スタック | — | 関数を抜けるまで | ❌ | ❌ |

> RP2040 では `.rodata` は XIP Flash に置かれる (SRAM を消費しない)。
> `.data` / `.bss` は SRAM に置かれる。

### 各パターンの使いどころ

```c
// ── グローバル変数 ──────────────────────────────────────

int g_count = 0;
// → .data (SRAM) / 他ファイルから extern int g_count; で参照可
//   モジュール間で共有する状態変数に使う

static int s_count = 0;
// → .data (SRAM) / このファイル内からしか見えない
//   ファイル内部の状態変数。extern で外から触らせたくないときに使う

const int C_MAX = 100;
// → .rodata (Flash) / 他ファイルから extern const int C_MAX; で参照可
//   大きなテーブルを共有したいときに使う (RAM を消費しない)

static const int SC_MAX = 100;
// → .rodata (Flash) / このファイル内からしか見えない
//   ファイル内部の定数。最も安全でよく使う組み合わせ

static const uint8_t sc_table[] = { 0x00, 0x01, 0xFF, ... };
// → .rodata (Flash) / 証明書・ルックアップテーブルなど大きな読み取り専用データに最適

// ── ローカル変数 ──────────────────────────────────────

void func(void) {
    int a = 0;
    // → スタック / 関数を抜けると消える / 毎回初期化される

    const int limit = 50;
    // → スタック / 関数を抜けると消える / 書き換え禁止
    //   コンパイラが定数として最適化する場合も多い

    static int call_count = 0;
    // → .bss (SRAM) / 関数を抜けても消えない / 初回だけ 0 で初期化
    //   呼び出し回数カウンタや状態保持に使う

    static const uint8_t lut[] = { 1, 2, 4, 8, 16 };
    // → .rodata (Flash) / 関数スコープなので外からは見えない
    //   関数内だけで使う小さなテーブルに最適
}
```

---

## `static` 修飾子 — 2 つの全く異なる意味

`static` はつける場所によって意味が変わる。混同しやすいため注意。

### ① グローバル `static` — カプセル化 (リンケージの制限)

```c
// foo.c
static int counter = 0;          // この翻訳単位(ファイル)からしか見えない
static void reset_counter(void);  // 他のファイルから呼べない

// main.c から counter や reset_counter は参照できない → リンクエラー
```

`static` をつけると **他の `.c` ファイルへの公開を遮断**できる。
割り込みハンドラやドライバ内部関数を `static` にして
意図しない外部呼び出しを防ぐのが定石。

```c
// uart_driver.c — 外部に見せたくない実装は全部 static
static void uart_irq_handler(void);   // 割り込みハンドラ (登録はするが直接呼ばせない)
static uint8_t tx_buf[64];            // ドライバ内部バッファ
static bool is_initialized = false;   // 内部状態

void uart_init(void) { ... }          // こちらだけ外部公開
```

### ② ローカル `static` — 静的領域への保存 (値を残す)

```c
uint32_t get_call_count(void) {
    static uint32_t count = 0;  // 初回のみ 0 で初期化、以降は値を保持
    return ++count;
}
```

通常のローカル変数はスタックに積まれ関数を抜けると消えるが、
`static` をつけると **`.bss` / `.data` (静的領域) に配置され、プログラム終了まで生き続ける**。
初期化式は最初の一度しか実行されない。

```c
// 典型例: 前回の ADC 値を保持してノイズフィルタ
uint16_t read_adc_filtered(void) {
    static uint16_t prev = 0;
    uint16_t raw = adc_read();
    prev = (prev + raw) / 2;  // prev は呼び出しをまたいで保持される
    return prev;
}
```

> **RAM 消費の注意**: ローカル `static` は静的領域を消費する。
> スタック節約のつもりで多用すると静的領域が圧迫される。
> また `static` ローカル変数は**再入不可** (割り込み + 通常処理で同じ関数が同時に走ると壊れる)。

---

## `volatile` — 最適化を止める

コンパイラはレジスタキャッシュや命令並べ替えで最適化を行う。
**ハードウェアレジスタ・割り込みフラグ・DMA バッファ**など、
プログラムの外から値が変わりうる変数には `volatile` が必須。

```c
// ❌ volatile なし → コンパイラが "値は変わらない" と判断してループを最適化除去する
bool flag = false;
void irq_handler(void) { flag = true; }
void wait_for_irq(void) {
    while (!flag) {}   // コンパイラが while(true){} に最適化するかもしれない
}

// ✅ volatile あり → 毎回メモリから読み直す
volatile bool flag = false;
void irq_handler(void) { flag = true; }
void wait_for_irq(void) {
    while (!flag) {}   // 必ず毎回メモリを参照する
}
```

### ハードウェアレジスタへの直接アクセス

```c
// メモリマップドレジスタは必ず volatile ポインタ経由で
#define GPIO_OUT  (*(volatile uint32_t *)0x400140CC)

GPIO_OUT = 0x01;   // 最適化で消えない
GPIO_OUT = 0x00;   // これも確実に実行される
```

### `volatile` と `const` の組み合わせ

```c
// 読み取り専用のハードウェアレジスタ (書いてはいけないが外部が変える)
#define GPIO_IN  (*(volatile const uint32_t *)0x400140D0)
```

> **`volatile` はスレッド安全を保証しない**。
> マルチコアや割り込みとの共有変数は
> `volatile` に加えて atomic 操作や spinlock が必要。

---

## `__attribute__` と `weak` 属性

GCC / Clang 拡張。組み込みで頻出する属性をまとめる。

### `__attribute__((weak))` — 弱いシンボル定義

`weak` 属性をつけた関数・変数は、**同名の強い定義が別ファイルにあればそちらが優先**される。
ライブラリのデフォルト実装をユーザーが上書きできる仕組みに使う。

```c
// library.c — デフォルト実装 (上書き可能)
__attribute__((weak))
void board_init(void) {
    // 何もしない デフォルト実装
}

// user_board.c — 強い定義 (こちらが優先される)
void board_init(void) {
    gpio_init(LED_PIN);     // 基板固有の初期化
    gpio_set_dir(LED_PIN, GPIO_OUT);
}
```

```
リンク時の優先度:
  強い定義 (通常の関数)  >  弱い定義 (__attribute__((weak)))
  両方ある → 強い方を使う
  weak しかない → weak を使う
```

pico-sdk では割り込みベクタのデフォルトハンドラが `weak` で定義されており、
ユーザーが同名の関数を定義するだけでオーバーライドできる。

```c
// pico-sdk 内部 (簡略化)
__attribute__((weak)) void isr_uart0(void) { /* デフォルト: 何もしない */ }

// ユーザーコード — 同名で strong 定義すれば自動的にこちらが使われる
void isr_uart0(void) {
    // 実際の UART 割り込み処理
}
```

### よく使う `__attribute__` 一覧

```c
// ── 最適化制御 ─────────────────────────────────────
__attribute__((optimize("O0")))         // この関数だけ最適化無効
void precise_delay(uint32_t us) { ... }

__attribute__((noinline))               // インライン展開を禁止
void debug_hook(void) { ... }

__attribute__((always_inline))          // 必ずインライン展開
static inline uint32_t fast_crc(uint32_t x) { ... }

// ── メモリ配置 ─────────────────────────────────────
__attribute__((aligned(4)))             // 4 バイト境界に整列
const uint8_t data[] = { ... };

__attribute__((packed))                 // パディングを除去
typedef struct { ... } packed_t;

__attribute__((section(".my_section"))) // 任意のセクションに配置
const uint8_t flash_data[] = { ... };

// ── シンボル管理 ────────────────────────────────────
__attribute__((weak))                   // 弱いシンボル (上書き可能)
void default_handler(void) { }

__attribute__((used))                   // 未使用でもバイナリに残す
static const char build_date[] = __DATE__;

__attribute__((unused))                 // 未使用警告を抑制
static void helper(void) { }

// ── 診断 ────────────────────────────────────────────
__attribute__((deprecated("use new_func instead")))
void old_func(void) { }                 // 呼び出すとコンパイル警告

__attribute__((noreturn))               // この関数は返らない
void fatal_error(void) { while(1){} }

// ── 関数呼び出し ────────────────────────────────────
__attribute__((constructor))            // main() より前に実行
static void early_init(void) { ... }
```

---

## 3 つのメモリ領域 — スタック / ヒープ / 静的領域

```
SRAM のレイアウトイメージ

  低アドレス ─────────────────────────────────
             [ .data  ] グローバル変数・ローカルstaticの実体
             [ .bss   ] ゼロ初期化グローバル変数
             ─ 静的領域 ここまで (リンク時にサイズ確定) ─

             [ heap   ] malloc/calloc で動的確保
                         ↓ 下から上へ伸びる

             (空き)

                         ↑ 上から下へ伸びる
             [ stack  ] 関数呼び出し・ローカル変数
  高アドレス ─────────────────────────────────
```

### 静的領域 (`.data` / `.bss`)

- **確保タイミング**: リンク時にサイズ確定、起動時に初期化
- **寿命**: プログラム終了まで
- **何が入るか**: グローバル変数、`static` 変数
- **注意**: ヒープ＋スタックを圧迫するため最小限に

### スタック領域

- **確保タイミング**: 関数呼び出し時に自動確保
- **寿命**: その関数 (ブロック) が終わるまで
- **何が入るか**: ローカル変数、関数の戻りアドレス、レジスタ退避
- **注意**: オーバーフローしてもエラーにならずデータを破壊する (サイレント破壊)

```c
void bad_function(void) {
    uint8_t big_buf[2048];  // スタックを 2 KB 消費 → オーバーフロー危険
}

// 代替: static にしてスタックを節約 (ただし静的領域を消費・再入不可)
void better_function(void) {
    static uint8_t big_buf[2048];
}
```

### ヒープ領域

- **確保タイミング**: `malloc` / `calloc` / `new` 呼び出し時
- **寿命**: `free` / `delete` まで
- **組み込みでは原則使わない**: 断片化でメモリが枯渇し、`malloc` が突然 `NULL` を返す。
  失敗チェックを怠ると即クラッシュ。

```c
// 組み込みで避けるべきパターン
uint8_t *p = malloc(256);   // 断片化・NULL 返却リスク
// p が NULL かチェックし忘れると即 HardFault

// 推奨: コンパイル時にサイズが決まるなら静的に確保
static uint8_t buf[256];
```

---

## ブロックスコープ `{}` と変数の寿命

C では `{}` を自由に書いてスコープを作れる。
リソース制限環境では**大きなローカル変数を早く解放**するのに使える。

```c
void process(void) {

    // ── ブロック 1: パース処理 ──────────────────
    {
        uint8_t parse_buf[512];    // ここでスタックに積まれる
        parse_data(parse_buf);
    }
    // ← ブロックを抜けた時点で parse_buf のスタック領域は解放される
    //   (コンパイラはこの領域を以降のローカル変数に再利用できる)

    // ── ブロック 2: 送信処理 ──────────────────
    {
        uint8_t send_buf[512];     // parse_buf と同じスタック領域を再利用可
        build_packet(send_buf);
        transmit(send_buf);
    }

    // parse_buf と send_buf が同時にスタックに載ることはない → 最大消費は 512 B
    // ブロックなしなら 1024 B 必要になる
}
```

> コンパイラが最適化すると実際には即解放されない場合もあるが、
> **意図を明示**するだけでも可読性・保守性が上がる。

### ブロックによる一時変数の隔離

```c
void update_state(void) {
    int status;

    {
        // このブロック内でしか使わない一時変数を隔離
        uint32_t raw_val = read_sensor();
        uint32_t calibrated = apply_calibration(raw_val);
        status = (calibrated > THRESHOLD) ? 1 : 0;
    }
    // raw_val, calibrated はここでは使えない → 誤用を防げる

    apply_status(status);
}
```

---

## `-O2` / `-Os` 最適化 — 何が消えて何が残るか

### 主な最適化と組み込みへの影響

| 最適化の種類 | `-O2` | `-Os` | 組み込みへの影響 |
|-------------|-------|-------|----------------|
| デッドコード除去 | ✅ | ✅ | 未使用関数・変数がバイナリから消える |
| インライン展開 | 積極的 | 控えめ | `-O2` はフラッシュ増加の可能性 |
| ループ展開 | ✅ | ❌ | `-O2` は速いが大きい |
| 定数畳み込み | ✅ | ✅ | コンパイル時に計算が完了する |
| 末尾呼び出し最適化 | ✅ | ✅ | スタック節約になる場合あり |

```
速度優先 → -O2  (フラッシュが余っている場合)
サイズ優先 → -Os (フラッシュが逼迫している場合)
```

### デッドコード除去 — `((void)0)` の意味

```c
// デバッグ用ログを本番では消したい場合
#ifdef DEBUG
  #define LOG(fmt, ...) printf(fmt, ##__VA_ARGS__)
#else
  #define LOG(fmt, ...) ((void)0)   // 何もしない式 — コンパイラが完全に除去
#endif

LOG("val = %d\n", x);  // リリースビルドでは機械語が 1 バイトも生成されない
```

`((void)0)` は「この式は意味を持たない」とコンパイラに伝える慣用表現。
`void` キャストにより「未使用の戻り値」警告も抑制できる。

```c
// 引数の未使用警告を抑制する慣用句 (割り込みハンドラでよく使う)
void gpio_irq_handler(uint gpio, uint32_t events) {
    (void)gpio;    // 使わない引数を明示的に無視
    (void)events;
    do_something();
}
```

---

## メモリ削減テクニック まとめ

### フラッシュ (ROM) の節約

```c
// ① 使わない機能を ifdef で除去
#ifndef DISABLE_WIFI
  #include "wifi_module.h"
#endif

// ② 文字列リテラルは自動で .rodata に入る (RAM は消費しない)
puts("Hello");  // "Hello" はフラッシュ上に置かれる

// ③ -Os でコンパイル
// CMakeLists.txt で個別上書き:
// target_compile_options(myapp PRIVATE -Os)
```

### SRAM の節約

```c
// ① 大きな定数テーブルは const で .rodata へ (RAM 消費ゼロ)
const uint16_t sin_table[256] = { ... };

// ② ビットフィールドで構造体を圧縮
typedef struct {
    uint8_t mode   : 2;  // 0-3 の値 → 2 bit
    uint8_t active : 1;  // bool → 1 bit
    uint8_t retry  : 4;  // 0-15 の値 → 4 bit
    uint8_t        : 1;  // パディング
} __attribute__((packed)) Config;  // 1 バイトに収まる

// ③ 同時に使わないバッファは union で共有
typedef union {
    uint8_t rx_buf[256];
    uint8_t tx_buf[256];  // rx と tx を同時に使わないなら同じ領域を共有
} SharedBuf;
static SharedBuf io;

// ④ スタック上の一時変数はブロックで寿命を絞る (前述)

// ⑤ malloc は使わない。静的確保で済むなら静的に
```

### スタックオーバーフロー対策

```c
// 危険: 大きな配列をスタックに置く
void risky(void) {
    char buf[1024];   // スタックを 1 KB 消費 — オーバーフロー注意
}

// 安全: static にしてスタックを節約 (再入不可になる点に注意)
void safe(void) {
    static char buf[1024];
}
```

---

## RP2040 固有 — セクションとメモリの対応

C コンパイラはグローバル変数をその性質によって異なるセクションに振り分ける。
RP2040 では各セクションが以下のメモリ領域にマップされる。

```
RP2040 アドレスマップ (抜粋)

  0x10000000 〜   XIP Flash (最大 16 MB)
                    .text    — コード (関数)
                    .rodata  — 読み取り専用データ (const グローバル)
                    .data    — 非 const グローバルの初期値コピー元

  0x20000000 〜   SRAM (264 KB)
                    .data    — 起動時にフラッシュからコピーされる
                    .bss     — ゼロ初期化変数
                    スタック / ヒープ
```

変数ごとの振り分けルール:

| 変数の書き方 | セクション | フラッシュ | RAM |
|-------------|-----------|-----------|-----|
| `const T x = ...;` | `.rodata` | ✅ 置かれる | 消費しない |
| `T x = ...;` | `.data` | 初期値のみ | ✅ コピーされる |
| `T x;` | `.bss` | 置かれない | ✅ ゼロ初期化 |

---

## RP2040 固有 — `const` グローバル変数がフラッシュに置かれる理由

### ① コンパイラが `.rodata` に入れる

`const` をつけると書き換えが禁止されるため、コンパイラは
`.data` ではなく `.rodata` セクションに配置する。

```c
// .rodata → フラッシュ上に置かれる (RAM を消費しない)
const uint8_t ca_cert_der[] = { 0x30, 0x82, ... };

// .data → フラッシュに初期値があり、起動時に SRAM へコピーされる (RAM を消費する)
uint8_t ca_cert_der[] = { 0x30, 0x82, ... };
```

### ② pico-sdk のリンカスクリプトが `.rodata` を XIP 領域に配置する

pico-sdk 付属の `memmap_default.ld` が `.rodata` を
`0x10000000` 番地から始まる XIP Flash 領域に割り当てる。
このリンカスクリプトは `CMakeLists_PicoW.txt` 経由で自動的に使われるため、
特別な設定を追加しなくても `const` をつけるだけでフラッシュに置かれる。

### ③ CPU は XIP キャッシュ経由でフラッシュを直接読む

RP2040 には **XIP (Execute In Place)** 機構があり、
フラッシュ上のアドレスをそのまま CPU のアドレス空間に見せる。
`.rodata` のデータは RAM へコピーされることなく、
フラッシュから直接読み出される。

```
CPU
 │
 ▼
XIP キャッシュ (8 KB)
 │  キャッシュミス時のみ
 ▼
QSPI Flash (ca_cert_der[] がここにある)
```

### まとめ

```c
const uint8_t ca_cert_der[] __attribute__((aligned(4))) = {
    0x30, 0x82, ...
};
```

この 1 行で起きていること:

1. `const` → コンパイラが `.rodata` セクションに配置する
2. `.rodata` → pico-sdk リンカスクリプトが XIP Flash 領域に配置する
3. XIP → CPU がフラッシュを直接読む (RAM へのコピーなし)
4. `aligned(4)` → XIP キャッシュのアクセスを 4 バイト境界に整列する

結果として、**SRAM を 1 バイトも消費せずにフラッシュ上のデータを参照できる**。
PicoW の SRAM は 264 KB しかないため、変化しない大きなデータ (証明書・テーブル等)
は積極的に `const` + フラッシュ配置にするとよい。

---

## RP2040 固有 — `__attribute__((aligned(4)))` の意味

フラッシュへの配置自体とは無関係で、**アクセス効率のための整列指定**。

RP2040 の XIP キャッシュは 4 バイト単位でフラッシュを読む。
アドレスが 4 バイト境界にそろっていないと、
1 回のアクセスが 2 回に分割されて読み出しが遅くなる場合がある。

```c
// 4 バイト境界に整列 → XIP アクセスが 1 回で済む (推奨)
const uint8_t data[] __attribute__((aligned(4))) = { ... };

// 整列なし → 境界をまたぐと 2 回に分割される可能性がある
const uint8_t data[] = { ... };
```

証明書データのようにまとまったバイト列を読む用途では
`aligned(4)` をつけておくのが無難。

RP2040 固有の追加設定:

```c
// スタックサイズを増やす (CMakeLists.txt)
// target_compile_definitions(myapp PRIVATE PICO_STACK_SIZE=0x1000)  // 4 KB

// -Os でコンパイル (pico-sdk デフォルト。2 MB フラッシュ向けに推奨)
// target_compile_options(myapp PRIVATE -Os)
```

---

## 参考

- RP2040 Datasheet — 2.6 XIP (Execute-in-Place)
- pico-sdk `src/rp2_common/pico_standard_link/memmap_default.ld`
- GCC Manual — 3.11 Options That Control Optimization (`-Os`, `-O2`)
- ARM Cortex-M0+ Technical Reference Manual — Memory Model
- ISO/IEC 9899:2011 (C11) — 6.7.3 Type qualifiers (`volatile`, `const`)
