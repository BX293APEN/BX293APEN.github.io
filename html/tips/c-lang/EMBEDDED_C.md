# C/C++ Notes (Additional)

<!--
---

## 目次

1. [整数型と符号なし整数のオーバーフロー](#整数型と符号なし整数のオーバーフロー)
2. [整数リテラルのサフィックス](#整数リテラルのサフィックス)
3. [定数定義 — `#define` と `enum`](#定数定義--define-と-enum)
4. [プリプロセッサ / マクロ](#プリプロセッサ--マクロ)
5. [可変引数関数 — `va_list` / `vsnprintf`](#可変引数関数--va_list--vsnprintf)
6. [時刻構造体と整形出力 — `struct tm` / `strftime`](#時刻構造体と整形出力--struct-tm--strftime)
7. [構造体 — 定義・初期化・アクセス](#構造体--定義初期化アクセス)
8. [関数ポインタ](#関数ポインタ)
9. [`const` / `static` / `static const`](#const--static--static-const)
10. [`volatile`](#volatile)
11. [`__attribute__` と `weak` 属性](#__attribute__-と-weak-属性)
12. [3 つのメモリ領域](#3-つのメモリ領域)
13. [ブロックスコープ `{}` と変数の寿命](#ブロックスコープ-と変数の寿命)
14. [`-O2` / `-Os` 最適化](#-o2---os-最適化)
15. [メモリ削減テクニック まとめ](#メモリ削減テクニック-まとめ)
16. [RP2040 固有](#rp2040-固有)
17. [インラインアセンブリ — `asm`](#インラインアセンブリ--asm)

---
-->

## 整数型と符号なし整数のオーバーフロー

### 標準整数型 (`<stdint.h>`)

C の基本型はプラットフォームによってサイズが変わるため、組み込みでは固定幅型を使うのが鉄則。

| 型 | バイト | 範囲 |
|---|---|---|
| `uint8_t` | 1 | `0` 〜 `255` |
| `uint16_t` | 2 | `0` 〜 `65,535` |
| `uint32_t` | 4 | `0` 〜 `4,294,967,295` |
| `uint64_t` | 8 | `0` 〜 `18,446,744,073,709,551,615` |
| `int8_t` | 1 | `-128` 〜 `127` |
| `int16_t` | 2 | `-32,768` 〜 `32,767` |
| `int32_t` | 4 | `-2,147,483,648` 〜 `2,147,483,647` |
| `int64_t` | 8 | `-9.2×10^18` 〜 `9.2×10^18` |

最大値・最小値マクロ (`UINT8_MAX` / `INT8_MIN` / `INT8_MAX` など) も `<stdint.h>` に定義済み。

### オーバーフロー挙動

| 型 | オーバーフロー時の動作 | 規格上の扱い |
|---|---|---|
| 符号なし整数 | `2^N` を法とするモジュロ演算でラップアラウンド | **未定義動作ではない** (C 規格で保証) |
| 符号あり整数 | 実装依存 (多くの場合折り返すが保証なし) | **未定義動作 (UB)** |

```c
// 符号なし — ラップアラウンド
uint8_t x = 255;  x++;   // 256 % 256 = 0  → x == 0
uint8_t y = 0;    y--;   // -1 % 256 = 255 → y == 255

// 符号あり — UB (やってはいけない)
int8_t a = 127;
a++;   // ❌ UB — コンパイラが何をしても良い

// ✅ 符号ありでインクリメントが必要なら範囲チェックを入れる
if (a < INT8_MAX) a++;

// 型変換の落とし穴
uint8_t  a = 200, b = 100;
uint8_t  r1 = a + b;              // ❌ 300 → 44 (オーバーフロー)
uint16_t r2 = (uint16_t)a + b;   // ✅ 300

// 符号ミスマッチの比較
int32_t  len  = -1;
uint32_t size = 10;
if (len < size) { }   // ❌ -1 が巨大な正数に変換されて条件が偽になる
```

---

## 整数リテラルのサフィックス

何もつけないと `int` (符号あり 32 bit) 扱い。大きな値・符号なし・64 bit が必要なときはサフィックスで明示する。

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
| なし (小数) | `double` | 8 | `3.14` |

> `long` は環境依存 (Windows 64 bit: 4 バイト / Linux 64 bit: 8 バイト)。組み込みでは `int32_t` / `uint32_t` を使うのが安全。

### なぜサフィックスが必要か

```c
// ① オーバーフロー防止
uint32_t ms  = 60 * 1000U;      // ✅ 1000U で unsigned に昇格して計算
uint32_t big = 3000UL * 1000;   // ✅ 明示的に unsigned long で計算

// ② #define での大きな値
#define TIMEOUT_MS   60000U        // unsigned
#define CPU_FREQ_HZ  125000000UL   // 125 MHz
#define MAX_SIZE     0xFFFFFFFFU   // 32 bit 全ビット 1

// ③ 64 bit シフト
uint64_t mask  = 1ULL << 32;   // ✅ 1ULL で 64 bit にしてからシフト
uint64_t mask2 = 1   << 32;    // ❌ 1 は 32 bit int → シフト結果が 0 (UB)

// ④ float / double の混在
float f  = 1.0 / 3.0;    // double 演算 → float に代入で精度落ち
float f2 = 1.0f / 3.0f;  // ✅ float のまま計算
```

---

## 定数定義 — `#define` と `enum`

### `#define` vs `enum` の比較

| 項目 | `#define` | `enum` |
|---|---|---|
| 型 | なし (テキスト置換) | `int` (コンパイラが管理) |
| デバッガ表示 | 値のみ | 名前が見える場合あり |
| スコープ | グローバル (ファイル全体) | 通常はグローバル |
| 主な用途 | ビットマスク・文字列・マクロ展開 | 状態機械・モード列挙 |
| 連番自動付与 | ❌ | ✅ |

```c
// #define — テキスト置換。型を持たない
#define MAX_RETRY    3
#define TIMEOUT_MS   1000
#define PI_APPROX    3.14159f
#define VERSION_STR  "1.0.0"
#define FLAG_READY   0x01
#define FLAG_BUSY    0x02
#define ALL_FLAGS    (FLAG_READY | FLAG_BUSY)

// enum — 連番自動付与。デバッガで名前が見える
typedef enum {
    STATE_IDLE = 0,
    STATE_CONNECTING,   // 1
    STATE_CONNECTED,    // 2
    STATE_ERROR,        // 3
} wifi_state_t;

// 途中から値を指定
typedef enum {
    LOG_NONE  = 0,
    LOG_ERROR = 1,
    LOG_WARN  = 2,
    LOG_INFO  = 4,
    LOG_DEBUG = 8,
} log_level_t;
```

---

## プリプロセッサ / マクロ

### 基本ディレクティブ一覧

| ディレクティブ | 意味 |
|---|---|
| `#define SYMBOL value` | マクロ定義 |
| `#undef SYMBOL` | マクロ定義を削除 |
| `#ifdef SYMBOL` | SYMBOL が定義されていれば |
| `#ifndef SYMBOL` | SYMBOL が定義されていなければ |
| `#if expr` | 数値式で比較 |
| `#elif expr` | else if |
| `#else` | それ以外 |
| `#endif` | 条件ブロック終端 |
| `#include <header>` | システムヘッダ (インクルードパスを検索) |
| `#include "header"` | ローカルヘッダ (カレントディレクトリ優先) |
| `#error "msg"` | コンパイルを強制停止 |
| `#warning "msg"` | 警告のみ出してコンパイル継続 (GCC 拡張、C23 で標準化) |
| `#pragma once` | インクルードガードの簡略版 |

### `#if` で使える演算子

| 演算子 | 説明 | 例 |
|---|---|---|
| `>` `>=` `<` `<=` `==` `!=` | 比較 | `#if VER_MAJOR >= 1` |
| `&&` | AND | `#if defined(X) && (VER >= 1)` |
| `\|\|` | OR | `#if defined(X) \|\| defined(Y)` |
| `!` | NOT | `#if !defined(RELEASE)` |
| `defined(SYM)` | 定義されているか (式中で使う) | `#if defined(X) && defined(Y)` |

> `#ifdef X && Y` は NG — `ifdef` は `&&` と組み合わせられない。式中では `defined()` を使う。

### 関数マクロ

| マクロ | 定義 | 用途 |
|---|---|---|
| `MAX(a,b)` | `((a) > (b) ? (a) : (b))` | 最大値 |
| `MIN(a,b)` | `((a) < (b) ? (a) : (b))` | 最小値 |
| `ABS(x)` | `((x) < 0 ? -(x) : (x))` | 絶対値 |
| `BIT(n)` | `(1u << (n))` | n ビット目を立てる |
| `ARRAY_SIZE(a)` | `(sizeof(a) / sizeof((a)[0]))` | 配列の要素数 |

```c
// ❌ カッコなし — 演算子優先度バグ
#define BAD_DOUBLE(x)  x * 2        // BAD_DOUBLE(1+1) → 1+1*2 = 3
// ✅ 全引数をカッコで囲む
#define GOOD_DOUBLE(x) ((x) * 2)    // GOOD_DOUBLE(1+1) → (1+1)*2 = 4
```

### 複数文マクロ — `do { } while(0)` イディオム

```c
// ❌ if-else で壊れる
#define BAD_LOG(x)  printf("val=%d\n", x); log_write(x)
// if (cond) BAD_LOG(v); → log_write は常に実行される

// ✅ do-while(0) で 1 文として扱う
#define LOG(x) \
    do { \
        printf("val=%d\n", (x)); \
        log_write((x)); \
    } while (0)
```

### 可変引数マクロ と特殊演算子

| 記法 | 意味 |
|---|---|
| `...` / `__VA_ARGS__` | 可変引数部分 |
| `##__VA_ARGS__` | 引数がゼロのとき直前のカンマを消す (GCC 拡張) |
| `__VA_OPT__(x)` | 可変引数が 1 つ以上あるとき `x` に展開 (C23 / GCC8+) |
| `#x` | 引数をそのまま文字列リテラルにする (文字列化) |
| `a##b` | トークン連結 |

```c
// デバッグログ (リリースビルドで完全消去)
#ifdef DEBUG
  #define DBG(fmt, ...)  printf("[DBG] " fmt "\n", ##__VA_ARGS__)
#else
  #define DBG(fmt, ...)  ((void)0)
#endif

// 位置情報付きエラーログ
#define ERR(fmt, ...) \
    printf("[ERR %s:%d] " fmt "\n", __FILE__, __LINE__, ##__VA_ARGS__)

// 文字列化と二重展開
#define STRINGIFY_INNER(x)  #x
#define STRINGIFY(x)        STRINGIFY_INNER(x)  // 二重展開が必要

#define VERSION  42
STRINGIFY_INNER(VERSION)   // → "VERSION"  ❌
STRINGIFY(VERSION)         // → "42"       ✅

// トークン連結
#define CONCAT_INNER(a, b)  a##b
#define CONCAT(a, b)        CONCAT_INNER(a, b)
```

### 定義済みマクロ

| マクロ | 展開例 | 意味 |
|---|---|---|
| `__FILE__` | `"main.c"` | ソースファイル名 |
| `__LINE__` | `42` | 行番号 |
| `__func__` | `"main"` | 関数名 (C99以降) |
| `__DATE__` | `"Jun  4 2026"` | コンパイル日 |
| `__TIME__` | `"12:34:56"` | コンパイル時刻 |
| `__COUNTER__` | `0`, `1`, `2` ... | 展開のたびに増える連番 |
| `__STDC_VERSION__` | `201112L` | C 規格バージョン (C11 = 201112L) |

### `_Static_assert` — コンパイル時アサート (C11)

```c
#include <assert.h>

// 構造体が 4 バイトか確認 (レジスタマップなど)
_Static_assert(sizeof(RegMap) == 4, "RegMap は 4 バイトである必要があります");

// C11 以降は static_assert() でも書ける (エイリアス)
static_assert(sizeof(void *) == 4, "このコードは 32 bit 環境専用です");
```

> `assert()` (実行時) と違い、ROM もフラッシュも消費しない。条件が偽だとコンパイルエラー。

### `_Pragma` — マクロ内からプラグマを発行 (C99)

```c
// #pragma はマクロ内に書けない → _Pragma("...") を使う
#define INCLUDE_EXTERNAL(header) \
    _Pragma("GCC diagnostic push") \
    _Pragma("GCC diagnostic ignored \"-Wsign-conversion\"") \
    _Pragma(#header) \
    _Pragma("GCC diagnostic pop")
```

---

## 可変引数関数 — `va_list` / `vsnprintf`

### `<stdarg.h>` の 4 マクロ

| マクロ | 役割 |
|---|---|
| `va_list ap` | 可変引数の「現在位置」を保持する型 |
| `va_start(ap, last_fixed)` | `ap` を初期化。最後の固定引数名を渡す |
| `va_arg(ap, type)` | 次の引数を指定型で取り出す (取り出すたびに位置が進む) |
| `va_copy(dst, src)` | `va_list` をコピー (2 回走査したいとき) |
| `va_end(ap)` | 後始末 (必ず呼ぶ) |

> `va_arg` の型指定は呼び出し側と一致させること。`float` は `double` に昇格されて積まれるため `va_arg(ap, double)` が正しい。

### `v` 系関数 — `va_list` をそのまま渡せる printf 族

| 通常版 | `va_list` 版 | 特記事項 |
|---|---|---|
| `printf` | `vprintf` | 標準出力に書式出力 |
| `sprintf` | `vsprintf` | バッファ長チェックなし ⚠️ |
| `snprintf` | `vsnprintf` | バッファ長を指定して安全に書式出力 ✅ |
| `fprintf` | `vfprintf` | ファイルに書式出力 |

### `vsnprintf` の引数と戻り値

```c
int vsnprintf(char *buf, size_t size, const char *fmt, va_list ap);
//            ↑書き込み先  ↑バッファサイズ  ↑書式文字列  ↑va_list

// 戻り値 = 「切り捨てなしなら何文字書き込まれるか」(C99)
// 戻り値 >= size なら切り捨てが起きている
// 末尾に必ず '\0' を付ける (最大 size-1 文字書き込む)
```

### プラットフォーム別の安全な実装

```c
// Windows MSVC と GCC/Clang の分岐
static int safe_vsnprintf(char *buf, size_t size, const char *fmt, va_list ap) {
#if defined(_MSC_VER)
    return _vsnprintf_s(buf, size, _TRUNCATE, fmt, ap);  // Windows MSVC
#else
    return vsnprintf(buf, size, fmt, ap);                 // GCC / Clang / pico-sdk
#endif
}
```

> `_vsnprintf_s` は MSVC 拡張。組み込み (pico-sdk / GCC) では使えない。`_TRUNCATE` を渡すと切り捨て許容動作 (= `vsnprintf` 互換) になる。

### 自作フォーマット関数の定石

```c
// 定石: vsnprintf でバッファに書式化 → 後から出力・転送・ログ蓄積
void my_log(const char *fmt, ...) {
    char buf[128];
    va_list ap;
    va_start(ap, fmt);
    int n = vsnprintf(buf, sizeof(buf), fmt, ap);   // バッファに書式化
    va_end(ap);
    if (n >= (int)sizeof(buf)) { /* 切り捨て発生 */ }
    uart_puts(buf);
}

// ❌ 同じ va_list を 2 回渡してはいけない
void bad(const char *fmt, ...) {
    va_list ap;
    va_start(ap, fmt);
    vsnprintf(buf1, sizeof(buf1), fmt, ap);  // ap が末尾まで進む
    vsnprintf(buf2, sizeof(buf2), fmt, ap);  // ❌ 未定義動作
    va_end(ap);
}

// ✅ 2 回使うなら va_copy
void good(const char *fmt, ...) {
    va_list ap, ap2;
    va_start(ap, fmt);
    va_copy(ap2, ap);
    vsnprintf(buf1, sizeof(buf1), fmt, ap);   // ap を消費
    vsnprintf(buf2, sizeof(buf2), fmt, ap2);  // ap2 を消費
    va_end(ap2);
    va_end(ap);
}

// __attribute__((format)) で printf 互換の型チェック
void log_impl(log_level_t lv, const char *file, int line, const char *fmt, ...)
    __attribute__((format(printf, 4, 5)));
// 数字の意味: 4 = fmt が第 4 引数 / 5 = 可変引数が第 5 引数から
```

---

## 時刻構造体と整形出力 — `struct tm` / `strftime`

### `struct tm` のメンバ

| メンバ | 範囲 | 注意点 |
|---|---|---|
| `tm_sec` | `[0, 60]` | 60 はうるう秒 |
| `tm_min` | `[0, 59]` | |
| `tm_hour` | `[0, 23]` | |
| `tm_mday` | `[1, 31]` | |
| `tm_mon` | `[0, 11]` | **0 始まり** (1月=0, 12月=11) |
| `tm_year` | 1900 からの差分 | **2024年 → 124** |
| `tm_wday` | `[0, 6]` | 0=日曜 |
| `tm_yday` | `[0, 365]` | 年内通算日 |
| `tm_isdst` | 1/0/-1 | 夏時間 / 通常 / 不明 |

### `time_t` ↔ `struct tm` の変換関数

| 関数 | 変換方向 | 備考 |
|---|---|---|
| `time(NULL)` | → `time_t` | 現在時刻 (Unix エポック秒) |
| `localtime(&t)` | `time_t` → `struct tm *` | ローカル時刻。静的バッファを返す (スレッド unsafe) |
| `gmtime(&t)` | `time_t` → `struct tm *` | UTC。同上 |
| `localtime_r(&t, &tm)` | `time_t` → `struct tm *` | POSIX。スレッドセーフ版 |
| `mktime(&tm)` | `struct tm` → `time_t` | ローカル時刻として解釈して変換 |
| `difftime(end, start)` | — | 秒単位の差 (`double`) |

### `strftime` の書式指定子

| 指定子 | 内容 | 例 |
|---|---|---|
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

```c
// 書式化の基本
char buf[64];
struct tm *t = localtime(&now);
strftime(buf, sizeof(buf), "%Y-%m-%d %H:%M:%S", t);  // → "2024-06-04 15:30:00"

// RTC から読んだ値で struct tm を組み立てる (組み込みでよくある)
struct tm rtc_time = {
    .tm_year  = 2024 - 1900,  // 1900 引く！
    .tm_mon   = 6 - 1,        // 1 引く！ (6月 → 5)
    .tm_mday  = 4,
    .tm_hour  = 15,
    .tm_min   = 30,
    .tm_sec   = 0,
    .tm_isdst = -1,
};
```

---

## 構造体 — 定義・初期化・アクセス

### アクセス演算子

| 演算子 | 使う状況 | 例 |
|---|---|---|
| `.` | 値 (実体) の場合 | `cfg.port` |
| `->` | ポインタ経由の場合 | `ptr->port` |

`->` は `(*ptr).port` の糖衣構文。

### 指示子初期化 (Designated Initializer, C99)

フィールド名を明示して初期化する。順番変更に強く、未指定フィールドは自動的に 0 になる。

```c
typedef struct {
    const char *server;
    uint16_t    port;
    const char *ssid;
    const char *password;
} wifi_config_t;

static const wifi_config_t cfg = {
    .server   = "192.168.10.64",
    .port     = 19080,
    .ssid     = "YOUR_SSID",
    .password = "YOUR_PASSWORD",
};
// 未指定フィールドは NULL / 0 になる
```

### `__attribute__((packed))` — パディング除去

```c
// 通常 (パディングあり)
typedef struct {
    uint8_t  a;     // 1 バイト
    // [3 バイトパディング]
    uint32_t b;     // 4 バイト
} normal_t;         // sizeof = 8

// packed (パディングなし) — 通信プロトコルのパケット定義に使う
typedef struct __attribute__((packed)) {
    uint8_t  a;     // 1 バイト
    uint32_t b;     // 4 バイト (1 バイト境界に配置)
} packed_t;         // sizeof = 5
// ⚠️ 非アライメントアクセスは一部 CPU で遅い・クラッシュする可能性あり
```

---

## 関数ポインタ

### 宣言・typedef・呼び出し

```c
// 宣言: 戻り値型 (*変数名)(引数型, ...)
int (*fp)(int, int);

// typedef で読みやすくする (推奨)
typedef int (*math_op_t)(int, int);
math_op_t op = add;
op(2, 3);   // → 5

// typedef によるコールバック型の定義
typedef void (*event_handler_t)(uint8_t event_id, void *user_data);
```

### ディスパッチテーブル

```c
typedef void (*cmd_handler_t)(void);

void cmd_start(void) { /* ... */ }
void cmd_stop(void)  { /* ... */ }
void cmd_reset(void) { /* ... */ }

static const cmd_handler_t dispatch_table[] = {
    [0] = cmd_start,
    [1] = cmd_stop,
    [2] = cmd_reset,
};
#define CMD_COUNT  ARRAY_SIZE(dispatch_table)

void handle_command(uint8_t cmd) {
    if (cmd < CMD_COUNT && dispatch_table[cmd] != NULL) {
        dispatch_table[cmd]();
    }
}
```

---

## `const` / `static` / `static const`

### 修飾子の組み合わせ早見表

| 書き方 | セクション | 保存先 | 寿命 | 他ファイルから見える？ | 書き換え可？ |
|---|---|---|---|---|---|
| `int x;` (グローバル) | `.bss` | SRAM | プログラム終了まで | ✅ (`extern` で) | ✅ |
| `int x = 1;` (グローバル) | `.data` | SRAM | プログラム終了まで | ✅ | ✅ |
| `static int x;` (グローバル) | `.bss` | SRAM | プログラム終了まで | ❌ このファイルのみ | ✅ |
| `const int x = 1;` (グローバル) | `.rodata` | Flash | プログラム終了まで | ✅ | ❌ |
| `static const int x = 1;` (グローバル) | `.rodata` | Flash | プログラム終了まで | ❌ このファイルのみ | ❌ |
| `int x;` (ローカル) | — | スタック | 関数を抜けるまで | ❌ | ✅ |
| `static int x;` (ローカル) | `.bss`/`.data` | SRAM | プログラム終了まで | ❌ | ✅ |
| `const int x = 1;` (ローカル) | — | スタック | 関数を抜けるまで | ❌ | ❌ |

> RP2040 では `.rodata` は XIP Flash に置かれる (SRAM を消費しない)。

### `static` の 2 つの意味

| 場所 | 意味 |
|---|---|
| グローバル / 関数定義の前 | **カプセル化** — 他の `.c` ファイルへの公開を遮断 (リンケージ制限) |
| ローカル変数の前 | **静的領域への保存** — 関数を抜けても値が残る (`.bss` / `.data`) |

### `static` 変数の初期値

初期化式を省略した `static` 変数は、C 規格により **必ずゼロで初期化される**。ゼロ初期化変数は `.bss` セクションに配置され、起動時にランタイム (crt0 など) がまとめてゼロクリアする。

| 書き方 | セクション | 初期値 | 備考 |
|---|---|---|---|
| `static T x;` | `.bss` | **0** (自動ゼロクリア) | 省略してもゼロ保証 |
| `static T x = 0;` | `.bss` | **0** (明示版) | 上と全く同じ意味 |
| `static T x = 1;` | `.data` | 1 | フラッシュからコピー |

グローバル変数も静的領域に置かれるため同じルールが適用される。

```c
// 初期値を「わざと 1」にする例 — 省略した場合との対比
uint32_t get_call_count(void) {
    static uint32_t count = 1;  // 初回のみ 1 で初期化、以降は値を保持
    return count++;
}

// 省略した場合は 0 で初期化されることが保証される
uint16_t read_adc_filtered(void) {
    static uint16_t prev;       // = 0  (省略 → 自動的にゼロ)
    uint16_t raw = adc_read();
    prev = (prev + raw) / 2;
    return prev;
}
// ⚠️ static ローカル変数は再入不可 (割り込み + 通常処理で同時実行すると壊れる)
```

---

## `volatile`

コンパイラのレジスタキャッシュや命令並べ替えを抑制する。ハードウェアレジスタ・割り込みフラグ・DMA バッファなど、プログラムの外から値が変わりうる変数に必須。

### `volatile` の用途

| 用途 | 説明 |
|---|---|
| 割り込みフラグ | 割り込みハンドラが書き換える変数 |
| ハードウェアレジスタ | メモリマップドレジスタへの直接アクセス |
| DMA バッファ | CPU 以外がメモリを書き換える領域 |
| マルチコア共有変数 | 別コアが書き換える変数 (+ atomic も必要) |

> **`volatile` はスレッド安全を保証しない**。マルチコアや割り込みとの共有変数は `volatile` に加えて atomic 操作や spinlock が必要。

```c
// ❌ volatile なし → while(true){} に最適化される可能性
bool flag = false;
void irq_handler(void) { flag = true; }
void wait(void) { while (!flag) {} }

// ✅ volatile あり → 毎回メモリから読み直す
volatile bool flag = false;

// メモリマップドレジスタ
#define GPIO_OUT  (*(volatile uint32_t *)0x400140CC)
GPIO_OUT = 0x01;   // 最適化で消えない

// 読み取り専用レジスタ (volatile + const)
#define GPIO_IN  (*(volatile const uint32_t *)0x400140D0)
```

---

## `__attribute__` と `weak` 属性

### よく使う `__attribute__` 一覧

| 属性 | 用途 |
|---|---|
| `__attribute__((weak))` | 弱いシンボル定義 — 強い定義があればそちらが優先される |
| `__attribute__((used))` | 未使用でもバイナリに残す |
| `__attribute__((unused))` | 未使用警告を抑制 |
| `__attribute__((noinline))` | インライン展開を禁止 |
| `__attribute__((always_inline))` | 必ずインライン展開 |
| `__attribute__((optimize("O0")))` | この関数だけ最適化無効 |
| `__attribute__((aligned(N)))` | N バイト境界に整列 |
| `__attribute__((packed))` | パディングを除去 |
| `__attribute__((section(".name")))` | 任意のセクションに配置 |
| `__attribute__((noreturn))` | この関数は返らない |
| `__attribute__((deprecated("msg")))` | 呼び出すとコンパイル警告 |
| `__attribute__((constructor))` | `main()` より前に実行 |
| `__attribute__((format(printf, m, n)))` | printf 互換の型チェック (`m`=fmtの引数位置, `n`=可変引数開始位置) |

### `__attribute__((weak))` の仕組み

```
リンク時の優先度:
  強い定義 (通常の関数)  >  弱い定義 (__attribute__((weak)))
  両方ある → 強い方を使う
  weak しかない → weak を使う
```

```c
// library.c — デフォルト実装 (上書き可能)
__attribute__((weak))
void board_init(void) { /* 何もしない */ }

// user_board.c — 強い定義。こちらが優先される
void board_init(void) {
    gpio_init(LED_PIN);
    gpio_set_dir(LED_PIN, GPIO_OUT);
}

// pico-sdk 活用例: 割り込みベクタのデフォルトハンドラは weak で定義されている
// → 同名の関数を定義するだけでオーバーライドできる
void isr_uart0(void) { /* 実際の UART 割り込み処理 */ }
```

---

## 3 つのメモリ領域

### 各領域の比較

| 領域 | 確保タイミング | 寿命 | 用途 | 組み込みでの注意 |
|---|---|---|---|---|
| 静的領域 (`.data`/`.bss`) | リンク時にサイズ確定、起動時に初期化 | プログラム終了まで | グローバル変数、`static` 変数 | ヒープ＋スタックを圧迫するため最小限に |
| スタック | 関数呼び出し時に自動確保 | その関数 (ブロック) が終わるまで | ローカル変数、戻りアドレス、レジスタ退避 | オーバーフローしてもエラーにならずサイレントにデータを破壊する |
| ヒープ | `malloc` / `calloc` 呼び出し時 | `free` まで | 動的確保 | **組み込みでは原則使わない** — 断片化で `malloc` が突然 `NULL` を返す |

```
SRAM のレイアウト (低アドレス → 高アドレス)
  [ .data  ]  グローバル変数・ローカル static の実体
  [ .bss   ]  ゼロ初期化グローバル変数
  ─── 静的領域 (リンク時にサイズ確定) ───
  [ heap   ]  ↓ 下から上へ伸びる
  (空き)
  [ stack  ]  ↑ 上から下へ伸びる
```

```c
// スタック消費の削減: static にして静的領域へ
void risky(void)  { uint8_t buf[2048]; ... }         // スタック 2 KB 消費
void better(void) { static uint8_t buf[2048]; ... }  // 静的領域に移動 (再入不可)

// ブロックスコープで大きなバッファの寿命を絞る
void process(void) {
    { uint8_t parse_buf[512]; parse_data(parse_buf); }
    // ← ブロックを抜けた時点でスタック解放。以降は再利用可
    { uint8_t send_buf[512];  build_packet(send_buf); transmit(send_buf); }
    // parse_buf と send_buf が同時にスタックに載らない → 最大消費 512 B
}
```

---

## `-O2` / `-Os` 最適化

### 最適化オプションの比較

| 最適化の種類 | `-O2` | `-Os` | 組み込みへの影響 |
|---|---|---|---|
| デッドコード除去 | ✅ | ✅ | 未使用関数・変数がバイナリから消える |
| インライン展開 | 積極的 | 控えめ | `-O2` はフラッシュ増加の可能性あり |
| ループ展開 | ✅ | ❌ | `-O2` は速いが大きい |
| 定数畳み込み | ✅ | ✅ | コンパイル時に計算が完了する |
| 末尾呼び出し最適化 | ✅ | ✅ | スタック節約になる場合あり |

> 速度優先 → `-O2` (フラッシュが余っている場合) / サイズ優先 → `-Os` (フラッシュが逼迫している場合)

### デッドコード除去と `((void)0)`

```c
// デバッグログを本番で完全消去
#ifdef DEBUG
  #define LOG(fmt, ...) printf(fmt, ##__VA_ARGS__)
#else
  #define LOG(fmt, ...) ((void)0)  // 機械語が 1 バイトも生成されない
#endif

// 未使用引数の警告を抑制 (割り込みハンドラでよく使う)
void gpio_irq_handler(uint gpio, uint32_t events) {
    (void)gpio;
    (void)events;
    do_something();
}
```

---

## メモリ削減テクニック まとめ

### フラッシュ (ROM) の節約

| テクニック | 説明 |
|---|---|
| `#ifdef` で機能を除去 | 未使用機能をビルドから除外する |
| 文字列リテラルは `.rodata` | `puts("Hello")` の `"Hello"` はフラッシュ上に置かれる (RAM 消費なし) |
| `-Os` でコンパイル | `CMakeLists.txt` で `target_compile_options(myapp PRIVATE -Os)` |

### SRAM の節約

| テクニック | 説明 |
|---|---|
| `const` でテーブルを `.rodata` へ | `const uint16_t sin_table[256]` → Flash 配置で RAM 消費ゼロ |
| ビットフィールドで構造体圧縮 | `uint8_t mode : 2` で 2 bit 単位に詰める |
| `union` でバッファ共有 | 同時に使わない rx/tx バッファを共有領域に収める |
| ブロックスコープで寿命を絞る | 大きなローカルバッファを早く解放する |
| `malloc` を使わない | 静的確保で済むなら静的に |

```c
// ビットフィールド
typedef struct {
    uint8_t mode   : 2;  // 0-3 → 2 bit
    uint8_t active : 1;  // bool → 1 bit
    uint8_t retry  : 4;  // 0-15 → 4 bit
    uint8_t        : 1;  // パディング
} __attribute__((packed)) Config;  // 1 バイトに収まる

// union でバッファ共有
typedef union {
    uint8_t rx_buf[256];
    uint8_t tx_buf[256];  // rx と tx は同時に使わない
} SharedBuf;
static SharedBuf io;
```

---

## RP2040 固有

### セクションとメモリの対応

| 変数の書き方 | セクション | Flash | RAM |
|---|---|---|---|
| `const T x = ...;` | `.rodata` | ✅ 置かれる | 消費しない |
| `T x = ...;` | `.data` | 初期値のみ | ✅ コピーされる |
| `T x;` | `.bss` | 置かれない | ✅ ゼロ初期化 |

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

### `const` グローバル変数がフラッシュに置かれる仕組み

```c
const uint8_t ca_cert_der[] __attribute__((aligned(4))) = { 0x30, 0x82, ... };
```

この 1 行で起きていること:

1. `const` → コンパイラが `.rodata` セクションに配置する
2. `.rodata` → pico-sdk リンカスクリプト (`memmap_default.ld`) が XIP Flash 領域に配置する
3. XIP (Execute In Place) → CPU がフラッシュを直接読む (RAM へのコピーなし)
4. `aligned(4)` → XIP キャッシュの 4 バイト単位アクセスを境界に整列して効率化する

結果として **SRAM を 1 バイトも消費せずにフラッシュ上のデータを参照できる**。

### その他の固有設定

```c
// スタックサイズを増やす (CMakeLists.txt)
// target_compile_definitions(myapp PRIVATE PICO_STACK_SIZE=0x1000)  // 4 KB

// -Os でコンパイル (pico-sdk デフォルト)
// target_compile_options(myapp PRIVATE -Os)
```

---

## インラインアセンブリ — `asm`

### 基本構文

| 記法 | 意味 |
|---|---|
| `asm("命令")` | 基本形 (副作用なし) |
| `asm volatile("命令")` | 並べ替え・削除を禁止 (ハードウェア操作では必須) |
| `__asm__ __volatile__("命令")` | 同上。厳密に標準 C に準拠したい場合 |

### 拡張 `asm` の構造

```c
asm volatile (
    "命令\n\t"          // アセンブリ本体。複数行は "\n\t" で区切る
    : 出力オペランド    // C変数 ← レジスタ
    : 入力オペランド    // レジスタ ← C変数
    : 破壊リスト        // この asm が書き換えるレジスタ・メモリを宣言
);

// 例: result = a + b (ARM Cortex-M)
uint32_t result, a = 10, b = 20;
asm volatile (
    "add %0, %1, %2"   // %0=出力, %1=入力1, %2=入力2
    : "=r"(result)     // 出力
    : "r"(a), "r"(b)   // 入力
);
```

### オペランド制約文字

| 制約 | 意味 | ARM | x86-64 |
|---|---|---|---|
| `r` | 汎用レジスタ | R0〜R12 | 任意 |
| `i` | 即値定数 | ✅ | ✅ |
| `m` | メモリアドレス | ✅ | ✅ |
| `=r` | 出力専用の汎用レジスタ | ✅ | ✅ |
| `+r` | 読み書き両用 (in-out) | ✅ | ✅ |
| `0`〜`9` | 指定番号の出力と同じレジスタ | ✅ | ✅ |
| `a` | `%rax` / `%eax` 固定 | — | ✅ |
| `b` | `%rbx` / `%ebx` 固定 | — | ✅ |
| `c` | `%rcx` / `%ecx` 固定 | — | ✅ |
| `d` | `%rdx` / `%edx` 固定 | — | ✅ |
| `S` | `%rsi` 固定 | — | ✅ |
| `D` | `%rdi` 固定 | — | ✅ |
| `A` | `%rax:%rdx` の 128 bit ペア | — | ✅ |

### `"memory"` 破壊宣言

```c
// "memory" を破壊リストに入れると:
//   「この asm はメモリを読み書きする可能性がある」とコンパイラに伝える
//   → asm の前後でメモリアクセスの並べ替えが禁止される (コンパイラバリア)
asm volatile ("dsb" ::: "memory");   // CPU バリア + コンパイラバリア
```

### ARM Cortex-M でよく使う命令

```c
// 割り込み有効/無効 (PRIMASK)
asm volatile ("cpsid i" ::: "memory");  // 全割り込み無効
asm volatile ("cpsie i" ::: "memory");  // 全割り込み有効

// 低消費電力待機
asm volatile ("wfi" ::: "memory");      // Wait For Interrupt
asm volatile ("wfe" ::: "memory");      // Wait For Event

// メモリバリア
asm volatile ("dsb" ::: "memory");      // Data Synchronization Barrier
asm volatile ("isb" ::: "memory");      // Instruction Synchronization Barrier
asm volatile ("dmb" ::: "memory");      // Data Memory Barrier

// 特殊レジスタの読み書き (MRS / MSR)
uint32_t sp;      asm volatile ("mov %0, sp"        : "=r"(sp));
uint32_t primask; asm volatile ("mrs %0, primask"   : "=r"(primask));
                  asm volatile ("msr primask, %0"   :: "r"(primask));

// CLZ — Count Leading Zeros (ビット演算高速化)
uint32_t n; asm volatile ("clz %0, %1" : "=r"(n) : "r"(x));
// 使用例: msb_pos = 31 - clz(x)  → 最上位の 1 のビット位置
```

### アーキテクチャ別 命令比較表

#### 基本情報

| | ARM Cortex-M (Thumb/Thumb-2) | x86-64 (AT&T 記法) |
|---|---|---|
| ビット幅 | 32 bit | 64 bit (32/16/8 bit も使用可) |
| 汎用レジスタ数 | R0〜R12 + SP/LR/PC = 16本 | `%rax` `%rbx` `%rcx` `%rdx` `%rsi` `%rdi` `%rbp` `%rsp` `%r8`〜`%r15` = 16本 |
| 命令フォーマット | `命令 dst, src1, src2` (3オペランド) | `命令 src, dst` (AT&T) / `命令 dst, src` (Intel) |
| 即値の書き方 | `#42` | `$42` (AT&T) |
| レジスタの書き方 | `r0` | `%rax` (AT&T) |
| 可変長命令 | 固定 16/32 bit (Thumb) | 1〜15 byte |
| 条件実行 | 多くの命令に条件付き実行あり (`moveq` 等) | `cmov` 系のみ |

#### 操作別比較 (ARM 組み込み / Linux x86-64 / Windows x86-64)

| 目的 | ARM 組み込み | Linux x86-64 | Windows x86-64 |
|---|---|---|---|
| **NOP** | `asm volatile ("nop")` | `asm volatile ("nop")` | `asm volatile ("nop")` / `__nop()` |
| **割り込み無効** | `asm volatile ("cpsid i" ::: "memory")` | `asm volatile ("cli" ::: "memory")` ※Ring0 | `asm volatile ("cli" ::: "memory")` ※Ring0 |
| **割り込み有効** | `asm volatile ("cpsie i" ::: "memory")` | `asm volatile ("sti" ::: "memory")` ※Ring0 | `asm volatile ("sti" ::: "memory")` ※Ring0 |
| **完全メモリバリア** | `asm volatile ("dsb" ::: "memory")` | `asm volatile ("mfence" ::: "memory")` | `asm volatile ("mfence" ::: "memory")` |
| **ロードバリア** | `asm volatile ("dmb" ::: "memory")` | `asm volatile ("lfence" ::: "memory")` | `asm volatile ("lfence" ::: "memory")` |
| **ストアバリア** | `asm volatile ("dmb" ::: "memory")` | `asm volatile ("sfence" ::: "memory")` | `asm volatile ("sfence" ::: "memory")` |
| **コンパイラのみバリア** | `asm volatile ("" ::: "memory")` | `asm volatile ("" ::: "memory")` | `asm volatile ("" ::: "memory")` |
| **命令同期** | `asm volatile ("isb" ::: "memory")` | (x86 では自動) | (x86 では自動) |
| **WFI スリープ** | `asm volatile ("wfi" ::: "memory")` | `hlt` (Ring0) / `pause` (スピン) | `hlt` (Ring0) / `pause` (スピン) |
| **WFE 待機** | `asm volatile ("wfe" ::: "memory")` | (相当命令なし) | (相当命令なし) |
| **スピン軽減** | `asm volatile ("yield")` | `asm volatile ("pause")` | `asm volatile ("pause")` / `YieldProcessor()` |
| **先頭ゼロカウント** | `clz %0, %1` | `bsrl` + 変換 | `_BitScanReverse()` |
| **末尾ゼロカウント** | (ソフト実装) | `bsfl` | `_BitScanForward()` |
| **セットビット数** | (ソフト実装) | `popcntl` | `__popcnt()` |
| **バイトスワップ** | `rev %0, %1` | `bswapl` | `_byteswap_ulong()` |
| **デバッグブレーク** | `asm volatile ("bkpt #0")` | `asm volatile ("int3")` | `asm volatile ("int3")` / `__debugbreak()` |
| **未定義命令トラップ** | `asm volatile ("udf #0")` | `ud2` | `ud2` |
| **テスト&セット** | `ldrex` / `strex` (M3以降) | `lock xchg` | `lock xchg` |
| **比較交換 (CAS)** | `ldrex` / `strex` | `lock cmpxchg` | `lock cmpxchg` |
| **高レベルAPI (割り込み)** | `pico-sdk: save_and_disable_interrupts()` | `local_irq_save()` (カーネル) | `KeAcquireSpinLock()` (WDK) |
| **高レベルAPI (バリア)** | `__dmb()` (pico-sdk) | `mb()` / `rmb()` / `wmb()` (カーネル) | `MemoryBarrier()` / `_ReadBarrier()` |
| **高レベルAPI (atomic)** | `pico-sdk: mutex_*` | `atomic_*` / `__sync_*` | `Interlocked*()` (WinAPI) |

> CLI/STI はユーザーランド (Ring3) では特権命令なのでクラッシュする。OS カーネルや特権モードのみ使用可。
> C11 の `<stdatomic.h>` を使えばアーキテクチャを意識せず書けるため、新規コードでは `atomic_*` を推奨。

#### `__builtin_*` — asm を書かずに済む GCC 組み込み関数

| 関数 | 機能 | 備考 |
|---|---|---|
| `__builtin_popcount(x)` | セットビット数 | ARM なら 1 命令 |
| `__builtin_clz(x)` | 先頭ゼロカウント | x=0 は未定義 |
| `__builtin_ctz(x)` | 末尾ゼロカウント | |
| `__builtin_bswap16(x)` | 16 bit バイトスワップ | `0x1234 → 0x3412` |
| `__builtin_bswap32(x)` | 32 bit バイトスワップ | `0x12345678 → 0x78563412` |
| `__builtin_unreachable()` | 到達不能を伝えて最適化 | |
| `__builtin_expect(expr, val)` | 分岐予測ヒント | 第 2 引数が予測値 |

### Intel 記法で書く — `.intel_syntax`

```c
// AT&T 記法 (GCC デフォルト)
asm volatile ("movl $42, %0" : "=r"(result));

// Intel 記法 — .intel_syntax noprefix / .att_syntax で囲む
asm volatile (
    ".intel_syntax noprefix \n\t"
    "mov %0, 42             \n\t"   // dst, src の順。$ % なし
    ".att_syntax            \n\t"   // 必ず AT&T に戻す
    : "=r"(result)
);
// ⚠️ .att_syntax で戻し忘れると後続のコンパイラ生成コードが Intel 記法として解釈されてリンクエラー
```

### インラインアセンブリの落とし穴

```c
// ❌ 破壊レジスタを宣言しないと他の変数が壊れる
asm volatile ("mov r0, #0");              // 危険
asm volatile ("mov r0, #0" ::: "r0");    // ✅ "r0" を破壊リストに列挙

// ❌ volatile を忘れると削除される
uint32_t dummy;
asm ("nop" : "=r"(dummy));       // 使わない出力 → 削除される可能性
asm volatile ("nop");            // ✅ volatile で削除を防ぐ

// ❌ "memory" 忘れでメモリアクセスが並べ替えられる
*reg = 1;
asm volatile ("dsb");                    // "memory" なし → 書き込みが移動する可能性
asm volatile ("dsb" ::: "memory");       // ✅

// Cortex-M0/M0+ では使えない命令
// sdiv / udiv (除算命令) — M3/M4 以降のみ
// ほとんどの DSP 命令 — M4/M7 以降のみ
```

### pico-sdk のラッパ関数 (asm 直書きより優先)

| ラッパ関数 | 対応する asm |
|---|---|
| `__dmb()` | `asm volatile ("dmb" ::: "memory")` |
| `__dsb()` | `asm volatile ("dsb" ::: "memory")` |
| `__isb()` | `asm volatile ("isb" ::: "memory")` |
| `__wfi()` | `asm volatile ("wfi" ::: "memory")` |
| `__wfe()` | `asm volatile ("wfe" ::: "memory")` |
| `save_and_disable_interrupts()` | PRIMASK 保存 + 割り込み無効 |
| `restore_interrupts(status)` | PRIMASK 復元 |

```c
#include "hardware/sync.h"
// 自分で asm を書く前に pico-sdk に同等機能がないか確認する
```

---

## CASLⅡ — レジスタ・命令対比

> 「第 1 引数」「第 2 引数」のような割り当ては **CPU の命令セットには存在しない**。`%rdi` も `%rax` もハードウェア的にはただの汎用レジスタで、「引数用」という意味は一切持たない。
> これは OS / コンパイラ間で事前に合意された **呼び出し規約 (calling convention) = ABI (Application Binary Interface)** によるソフトウェア上の取り決め:
> - x86-64 Windows : Microsoft x64 calling convention (Windows用レジスタ使用規約)
> - x86-64 Linux : System V AMD64 ABI (Linux用レジスタ使用規約)
>
> コンパイラがこの規約通りにコードを生成するからこそ、別々にコンパイル・アセンブルされた関数同士が正しく値を受け渡しできる。

### レジスタ・フラグ比較

| 名称 | CASLⅡ | ARM Cortex-M | x86-64 Windows | x86-64 Linux |
|---|---|---|---|---|
| 汎用レジスタ | `GR0`〜`GR7` (8 本) | `R0`〜`R12` + `SP`/`LR`/`PC` (16 本) | 下表参照 (16 本) | 下表参照 (16 本) |
| 第 1 引数 / 戻り値 | `GR0` / `GR0` | `R0` / `R0` | `%rcx` / `%rax` | `%rdi` / `%rax` |
| 第 2 引数 | `GR1` | `R1` | `%rdx` | `%rsi` |
| 第 3 引数 | `GR2` | `R2` | `%r8` | `%rdx` |
| 第 4 引数 | `GR3` | `R3` | `%r9` | `%rcx` |
| 第 5 引数 | — | — | スタック | `%r8` |
| 第 6 引数 | — | — | スタック | `%r9` |
| 呼び出し保存 | (概念なし) | `R4`〜`R11` | `%rbx` `%rbp` `%rsi` `%rdi` `%r12`〜`%r15` | `%rbx` `%rbp` `%r12`〜`%r15` |
| スタックポインタ | `SP` (`#9000` 開始想定) | `SP` (`R13`) | `%rsp` | `%rsp` |
| 戻りアドレス | (スタック) | `LR` (`R14`) | (スタック上) | (スタック上) |
| プログラムカウンタ | `PC` (`#8000` 開始想定) | `PC` (`R15`) | `%rip` | `%rip` |
| フラグレジスタ | `FR` (`SF`/`OF`/`ZF` の 3 ビット) | `APSR` (`N`/`Z`/`C`/`V`) | `RFLAGS` | `RFLAGS` |
| 符号フラグ | `SF` — 最上位ビットが `1` のとき立つ | `N` (Negative) | `SF` (Sign) | `SF` (Sign) |
| ゼロフラグ | `ZF` — 全ビット `0` のとき立つ | `Z` (Zero) | `ZF` (Zero) | `ZF` (Zero) |
| オーバーフローフラグ | `OF` — 算術: −32768〜32767 / 論理: 0〜65535 を超えたとき立つ | `V` (Overflow) | `OF` (Overflow) | `OF` (Overflow) |
| キャリーフラグ | (概念なし) | `C` (Carry) | `CF` (Carry) | `CF` (Carry) |

### x86-64 汎用レジスタ一覧

| レジスタ | 32 bit | 16 bit | 8 bit (下位) | 役割 / 慣例 (Linux) | 役割 / 慣例 (Windows) | 呼び出し保存 (Linux) | 呼び出し保存 (Windows) | 自由に読み書き可能 | 無条件に自由 |
|---|---|---|---|---|---|---|---|---|---|
| `%rax` | `%eax` | `%ax` | `%al` | 戻り値 / アキュムレータ | 戻り値 / アキュムレータ | ❌ caller-saved | ❌ caller-saved | ❌ | ❌ |
| `%rbx` | `%ebx` | `%bx` | `%bl` | 汎用 (用途自由) | 汎用 (用途自由) | ✅ callee-saved | ✅ callee-saved | ✅ | ❌ |
| `%rcx` | `%ecx` | `%cx` | `%cl` | 第 4 引数 / ループカウンタ、シフト演算の回数指定 (`CL`) | 第 1 引数 / ループカウンタ、シフト演算の回数指定 (`CL`) | ❌ caller-saved | ❌ caller-saved | ❌ | ❌ |
| `%rdx` | `%edx` | `%dx` | `%dl` | 第 3 引数 / 128 bit 戻り値の上位、掛け算・割り算の補助、I/O ポートのアドレス指定 (`DX`) | 第 2 引数 / 掛け算・割り算の補助、I/O ポートのアドレス指定 (`DX`) | ❌ caller-saved | ❌ caller-saved | ❌ | ❌ |
| `%rsi` | `%esi` | `%si` | `%sil` | 第 2 引数 / ソースインデックス (文字列操作) | 汎用 (非引数) / ソースインデックス (文字列操作) | ❌ caller-saved | ✅ callee-saved | ❌ | ❌ |
| `%rdi` | `%edi` | `%di` | `%dil` | 第 1 引数 / デスティネーションインデックス (文字列操作) | 汎用 (非引数) / デスティネーションインデックス (文字列操作) | ❌ caller-saved | ✅ callee-saved | ❌ | ❌ |
| `%rbp` | `%ebp` | `%bp` | `%bpl` | ベースポインタ (フレームポインタ) | ベースポインタ (フレームポインタ) | ✅ callee-saved | ✅ callee-saved | ✅ | ❌ |
| `%rsp` | `%esp` | `%sp` | `%spl` | **スタックポインタ** (直接操作は原則禁止) | **スタックポインタ** (直接操作は原則禁止) | ✅ callee-saved | ✅ callee-saved | ❌ | ❌ |
| `%r8` | `%r8d` | `%r8w` | `%r8b` | 第 5 引数 | 第 3 引数 | ❌ caller-saved | ❌ caller-saved | ✅ | ✅ |
| `%r9` | `%r9d` | `%r9w` | `%r9b` | 第 6 引数 | 第 4 引数 | ❌ caller-saved | ❌ caller-saved | ✅ | ✅ |
| `%r10` | `%r10d` | `%r10w` | `%r10b` | syscall で第 4 引数 (Linux カーネル) / 汎用 | 汎用 | ❌ caller-saved | ❌ caller-saved | ✅ | ✅ |
| `%r11` | `%r11d` | `%r11w` | `%r11b` | 汎用 / syscall がフラグ保存に使用 | 汎用 | ❌ caller-saved | ❌ caller-saved | ❌ | ❌ |
| `%r12` | `%r12d` | `%r12w` | `%r12b` | 汎用 (用途自由) | 汎用 (用途自由) | ✅ callee-saved | ✅ callee-saved | ✅ | ❌ |
| `%r13` | `%r13d` | `%r13w` | `%r13b` | 汎用 (用途自由) | 汎用 (用途自由) | ✅ callee-saved | ✅ callee-saved | ✅ | ❌ |
| `%r14` | `%r14d` | `%r14w` | `%r14b` | 汎用 (用途自由) | 汎用 (用途自由) | ✅ callee-saved | ✅ callee-saved | ✅ | ❌ |
| `%r15` | `%r15d` | `%r15w` | `%r15b` | 汎用 (用途自由) | 汎用 (用途自由) | ✅ callee-saved | ✅ callee-saved | ✅ | ❌ |
| `%rip` | — | — | — | **命令ポインタ** (直接書き込み不可 / `jmp`/`call`/`ret` で変化) | **命令ポインタ** (直接書き込み不可 / `jmp`/`call`/`ret` で変化) | — | — | ❌ | ❌ |

> **caller-saved** = 呼び出し元が保存する責任 (関数呼び出し後に値が壊れていると思え)
> **callee-saved** = 呼び出された関数が保存・復元する責任 (関数呼び出し後も値が保たれる)
>
> `%rsi` / `%rdi` は Linux では引数レジスタのため caller-saved、Windows では非引数の汎用レジスタとして callee-saved という違いがある。
>
> **「自由に読み書き可能」** = 命令セットレベルで暗黙の用途を持たないレジスタ (`ENTER`/`LEAVE` (`%rbp`) のようなほぼ使われないレガシー命令は対象外)。
> - `%rax` ❌: `MUL`/`DIV`/`CDQ` 系の暗黙オペランド
> - `%rcx` ❌: `LOOP`/`REP` の暗黙カウンタ、可変シフトの回数指定 (`CL`)、加えて `SYSCALL` 命令が戻り先 `RIP` を退避
> - `%rdx` ❌: `MUL`/`DIV` の上位ビット、`IN`/`OUT` のポート番号指定
> - `%rsi` / `%rdi` ❌: 文字列命令 (`MOVS`/`CMPS`/`STOS` 等) の暗黙ポインタ
> - `%rsp` ❌: `PUSH`/`POP`/`CALL`/`RET`/`INT` などスタック操作命令が暗黙に使用
> - `%r11` ❌: `SYSCALL`/`SYSRET` 命令が `RFLAGS` の退避に使用
> - `%r10` ✅: Linux の syscall 呼び出し規約で第 4 引数に使われるが、これは `SYSCALL` が `%rcx`/`%r11` を破壊するためカーネルがソフトウェア的に代用しているだけで、ハードウェアによる強制ではない
>
> **「無条件に自由」** = 自由に読み書き可能 ✅ かつ 呼び出し保存 (両OS) ❌ (= caller-saved) の積。命令的にもABI的にも一切の制約がなく、保存も復元も不要 (`%r8` `%r9` `%r10` のみ)。
>
> `%eax` など 32 bit 副レジスタへの書き込みは上位 32 bit を自動ゼロクリアする。
> `%ax` `%al` など 16/8 bit への書き込みは上位ビットを変更しない点に注意。

### CASLⅡ vs ARM vs x86-64 の対比

| 目的 | CASLⅡ | ARM Cortex-M | x86-64 Windows | x86-64 Linux |
|---|---|---|---|---|
| 無操作 | `NOP` | `nop` | `nop` | `nop` |
| メモリから読む | `LD GR1, addr` | `ldr r0, [addr]` | `movl addr, %eax` | `movl addr, %eax` |
| メモリへ書く | `ST GR1, addr` | `str r0, [addr]` | `movl %eax, addr` | `movl %eax, addr` |
| レジスタ間コピー | `LD GR1, GR2` | `mov r0, r1` | `movl %ebx, %eax` | `movl %ebx, %eax` |
| 算術加算 | `ADDA GR1, GR2` | `add r0, r0, r1` | `addl %ebx, %eax` | `addl %ebx, %eax` |
| 算術減算 | `SUBA GR1, GR2` | `sub r0, r0, r1` | `subl %ebx, %eax` | `subl %ebx, %eax` |
| ビット AND | `AND GR1, GR2` | `and r0, r0, r1` | `andl %ebx, %eax` | `andl %ebx, %eax` |
| ビット OR | `OR GR1, GR2` | `orr r0, r0, r1` | `orl %ebx, %eax` | `orl %ebx, %eax` |
| ビット XOR | `XOR GR1, GR2` | `eor r0, r0, r1` | `xorl %ebx, %eax` | `xorl %ebx, %eax` |
| 算術左シフト | `SLA GR1, n` | `lsl r0, r0, #n` | `sall $n, %eax` | `sall $n, %eax` |
| 論理右シフト | `SRL GR1, n` | `lsr r0, r0, #n` | `shrl $n, %eax` | `shrl $n, %eax` |
| 比較 | `CPA GR1, GR2` | `cmp r0, r1` | `cmpl %ebx, %eax` | `cmpl %ebx, %eax` |
| 無条件分岐 | `JUMP addr` | `b addr` | `jmp addr` | `jmp addr` |
| ゼロなら分岐 | `JZE addr` | `beq addr` | `je addr` | `je addr` |
| 非ゼロなら分岐 | `JNZ addr` | `bne addr` | `jne addr` | `jne addr` |
| 負数なら分岐 | `JMI addr` | `bmi addr` | `js addr` | `js addr` |
| オーバーフロー分岐 | `JOV addr` | `bvs addr` | `jo addr` | `jo addr` |
| スタックへ積む | `PUSH addr` | `push {r0}` | `pushq %rax` | `pushq %rax` |
| スタックから取る | `POP GR1` | `pop {r0}` | `popq %rax` | `popq %rax` |
| サブルーチン呼出 | `CALL addr` | `bl addr` | `call addr` | `call addr` |
| サブルーチン復帰 | `RET` | `bx lr` | `ret` | `ret` |
| システムコール | `SVC addr` | `svc #0` | `syscall` ※Win は通常 WinAPI 経由 | `syscall` |
| 割り込み制御 | (概念なし) | `cpsid i` / `cpsie i` | `cli` / `sti` ※Ring0 | `cli` / `sti` ※Ring0 |
| メモリバリア | (概念なし) | `dsb` / `dmb` / `isb` | `mfence` / `lfence` / `sfence` | `mfence` / `lfence` / `sfence` |

> ARM の `SVC` 命令 (Supervisor Call) は CASLⅡ の `SVC` と名前まで同じ。どちらも「OS や監視プログラムに処理を委譲する」という同じ目的を持つ。

---

## 参考

- RP2040 Datasheet — 2.6 XIP (Execute-in-Place)
- pico-sdk `src/rp2_common/pico_standard_link/memmap_default.ld`
- GCC Manual — 3.11 Options That Control Optimization (`-Os`, `-O2`)
- ARM Cortex-M0+ Technical Reference Manual — Memory Model
- ISO/IEC 9899:2011 (C11) — 6.7.3 Type qualifiers (`volatile`, `const`)
