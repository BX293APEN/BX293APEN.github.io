# LaTeX 書き方一覧

## 基本

| 説明 | 書き方 | 数式 | 備考 |
| --- | --- | --- | --- |
| 累乗(上付き) | `\begin{equation} x^{2} \end{equation}` | <div class="texClass">\begin{equation} x^{2} \end{equation}</div> | `^` の後ろが上付きになる。2文字以上は `{ }` で囲む |
| 添え字(下付き) | `\begin{equation} x_{i} \end{equation}` | <div class="texClass">\begin{equation} x_{i} \end{equation}</div> | `_` の後ろが下付きになる。2文字以上は `{ }` で囲む |
| 上付きと下付きの併用 | `\begin{equation} x_{i}^{2} \end{equation}` | <div class="texClass">\begin{equation} x_{i}^{2} \end{equation}</div> | 順序はどちらが先でもよい |
| 指数の中に累乗がある式 | `\begin{equation} e^{-x^{2}} \end{equation}` | <div class="texClass">\begin{equation} e^{-x^{2}} \end{equation}</div> | `{ }` を入れ子にする |
| 分数 | `\begin{equation} \frac{a}{b} \end{equation}` | <div class="texClass">\begin{equation} \frac{a}{b} \end{equation}</div> | 文中では小さく、独立した数式では大きく表示される |
| 分数(常に大きい表示) | `\begin{equation} \dfrac{a}{b} \end{equation}` | <div class="texClass">\begin{equation} \dfrac{a}{b} \end{equation}</div> | 文中や根号の中でも大きく表示される |
| 分数(常に小さい表示) | `\begin{equation} \tfrac{a}{b} \end{equation}` | <div class="texClass">\begin{equation} \tfrac{a}{b} \end{equation}</div> | 独立した数式でも小さく表示される |
| 平方根(ルート) | `\begin{equation} \sqrt{\mathstrut x} \end{equation}` | <div class="texClass">\begin{equation} \sqrt{\mathstrut x} \end{equation}</div> | `\mathstrut` を入れて、文字による根号の高さの違いをなくす |
| 立方根(n 乗根) | `\begin{equation} \sqrt[3]{\mathstrut x} \end{equation}` | <div class="texClass">\begin{equation} \sqrt[3]{\mathstrut x} \end{equation}</div> | `[ ]` に根の次数を書く。`\mathstrut` で高さをそろえる |
| ルートの中に式を入れる | `\begin{equation} \sqrt{\mathstrut x^{2}+y^{2}} \end{equation}` | <div class="texClass">\begin{equation} \sqrt{\mathstrut x^{2}+y^{2}} \end{equation}</div> | 根号の長さは中身に合わせて伸びる。`\mathstrut` で高さをそろえる |
| 二項係数(組み合わせ) | `\begin{equation} \binom{n}{k} \end{equation}` | <div class="texClass">\begin{equation} \binom{n}{k} \end{equation}</div> |  |

### 根号のずれ補正

| 説明 | 書き方 | 数式 | 備考 |
| --- | --- | --- | --- |
| 根号の高さが文字ごとに違う | `\begin{equation} \sqrt{\mathstrut a}\sqrt{\mathstrut b}\sqrt{\mathstrut x} \end{equation}` | <div class="texClass">\begin{equation} \sqrt{\mathstrut a}\sqrt{\mathstrut b}\sqrt{\mathstrut x} \end{equation}</div> | 各根号の中に `\mathstrut` を入れ、`(` と同じ高さの支柱で全部そろえる |
| 根号を隣の項と同じ高さにしたい | `\begin{equation} \sqrt{\vphantom{b}a}+\sqrt{b} \end{equation}` | <div class="texClass">\begin{equation} \sqrt{\vphantom{b}a}+\sqrt{b} \end{equation}</div> | 背の低い文字の側に、背の高い文字を `\vphantom` で入れて高さを合わせる |
| 下付き文字で根号が深くなる | `\begin{equation} \sqrt{\smash[b]{x_{i}}} \end{equation}` | <div class="texClass">\begin{equation} \sqrt{\smash[b]{x_{i}}} \end{equation}</div> | `\smash[b]` で下側の深さだけ 0 にする(上の高さは残す) |
| 根号内の分数が小さい | `\begin{equation} \sqrt{\dfrac{a}{b}} \end{equation}` | <div class="texClass">\begin{equation} \sqrt{\dfrac{a}{b}} \end{equation}</div> | `\frac` を `\dfrac` に替える |
| 根号が分数に食い込む | `\begin{equation} \sqrt{\frac{a}{b}\vphantom{\Big\vert}} \end{equation}` | <div class="texClass">\begin{equation} \sqrt{\frac{a}{b}\vphantom{\Big\vert}} \end{equation}</div> | 分数の後ろに `\vphantom{\Big\vert}` を入れ、根号の高さを確保する |

## 総和・積分・極限

| 説明 | 書き方 | 数式 | 備考 |
| --- | --- | --- | --- |
| 総和(シグマ) | `\begin{equation} \sum_{i=1}^{n} a_i \end{equation}` | <div class="texClass">\begin{equation} \sum_{i=1}^{n} a_i \end{equation}</div> | `_` が下端、`^` が上端 |
| 総乗(パイ) | `\begin{equation} \prod_{i=1}^{n} a_i \end{equation}` | <div class="texClass">\begin{equation} \prod_{i=1}^{n} a_i \end{equation}</div> |  |
| 定積分 | `\begin{equation} \int_{a}^{b} f(x)\,dx \end{equation}` | <div class="texClass">\begin{equation} \int_{a}^{b} f(x)\,dx \end{equation}</div> | `\,` で被積分関数と `dx` の間に細い空白を入れる |
| 二重積分 | `\begin{equation} \iint_{D} f\,dA \end{equation}` | <div class="texClass">\begin{equation} \iint_{D} f\,dA \end{equation}</div> |  |
| 周回積分(閉曲線に沿った線積分) | `\begin{equation} \oint_{C} \vec{F}\cdot d\vec{r} \end{equation}` | <div class="texClass">\begin{equation} \oint_{C} \vec{F}\cdot d\vec{r} \end{equation}</div> |  |
| 極限 | `\begin{equation} \lim_{x \to 0} \frac{\sin x}{x} \end{equation}` | <div class="texClass">\begin{equation} \lim_{x \to 0} \frac{\sin x}{x} \end{equation}</div> | 独立した数式では `x \to 0` が真下に付く |
| 導関数(微分) | `\begin{equation} \frac{d}{dx} f(x) \end{equation}` | <div class="texClass">\begin{equation} \frac{d}{dx} f(x) \end{equation}</div> |  |
| 偏微分 | `\begin{equation} \frac{\partial f}{\partial x} \end{equation}` | <div class="texClass">\begin{equation} \frac{\partial f}{\partial x} \end{equation}</div> |  |
| ナブラ(勾配) | `\begin{equation} \nabla f \end{equation}` | <div class="texClass">\begin{equation} \nabla f \end{equation}</div> |  |

## 括弧

| 説明 | 書き方 | 数式 | 備考 |
| --- | --- | --- | --- |
| 丸括弧(高さ自動調整) | `\begin{equation} \left( \frac{a}{b} \right) \end{equation}` | <div class="texClass">\begin{equation} \left( \frac{a}{b} \right) \end{equation}</div> | `\left` と `\right` は必ず対にする |
| 角括弧(高さ自動調整) | `\begin{equation} \left[ \frac{a}{b} \right] \end{equation}` | <div class="texClass">\begin{equation} \left[ \frac{a}{b} \right] \end{equation}</div> |  |
| 波括弧(高さ自動調整) | `\begin{equation} \left\{ \frac{a}{b} \right\} \end{equation}` | <div class="texClass">\begin{equation} \left\{ \frac{a}{b} \right\} \end{equation}</div> | `{` `}` は `\{` `\}` と書く |
| 絶対値 | `\begin{equation} \lvert x \rvert \end{equation}` | <div class="texClass">\begin{equation} \lvert x \rvert \end{equation}</div> | 縦線を直接書くより間隔が正しくなる |
| ノルム | `\begin{equation} \lVert x \rVert \end{equation}` | <div class="texClass">\begin{equation} \lVert x \rVert \end{equation}</div> |  |
| 内積(山括弧) | `\begin{equation} \langle x, y \rangle \end{equation}` | <div class="texClass">\begin{equation} \langle x, y \rangle \end{equation}</div> |  |
| 床関数(切り捨て) | `\begin{equation} \lfloor x \rfloor \end{equation}` | <div class="texClass">\begin{equation} \lfloor x \rfloor \end{equation}</div> |  |
| 天井関数(切り上げ) | `\begin{equation} \lceil x \rceil \end{equation}` | <div class="texClass">\begin{equation} \lceil x \rceil \end{equation}</div> |  |
| 括弧の大きさを指定(大) | `\begin{equation} \bigl( x \bigr) \end{equation}` | <div class="texClass">\begin{equation} \bigl( x \bigr) \end{equation}</div> | `\big` `\Big` `\bigg` `\Bigg` の順に大きくなる。`l` は左、`r` は右 |
| 括弧の大きさを指定(より大) | `\begin{equation} \Bigl( x \Bigr) \end{equation}` | <div class="texClass">\begin{equation} \Bigl( x \Bigr) \end{equation}</div> |  |

## ギリシャ文字

| 説明 | 書き方 | 数式 | 備考 |
| --- | --- | --- | --- |
| ギリシャ小文字(アルファ〜デルタ) | `\begin{equation} \alpha \beta \gamma \delta \end{equation}` | <div class="texClass">\begin{equation} \alpha \beta \gamma \delta \end{equation}</div> |  |
| ギリシャ小文字(イプシロン〜イータ) | `\begin{equation} \epsilon \varepsilon \zeta \eta \end{equation}` | <div class="texClass">\begin{equation} \epsilon \varepsilon \zeta \eta \end{equation}</div> | `\epsilon` と `\varepsilon` は字形違い |
| ギリシャ小文字(シータ〜ミュー) | `\begin{equation} \theta \vartheta \lambda \mu \end{equation}` | <div class="texClass">\begin{equation} \theta \vartheta \lambda \mu \end{equation}</div> | `\vartheta` は `\theta` の異体字 |
| ギリシャ小文字(パイ〜タウ) | `\begin{equation} \pi \rho \sigma \tau \end{equation}` | <div class="texClass">\begin{equation} \pi \rho \sigma \tau \end{equation}</div> |  |
| ギリシャ小文字(ファイ〜オメガ) | `\begin{equation} \phi \varphi \chi \psi \omega \end{equation}` | <div class="texClass">\begin{equation} \phi \varphi \chi \psi \omega \end{equation}</div> | `\phi` と `\varphi` は字形違い |
| ギリシャ大文字(ガンマ〜ラムダ) | `\begin{equation} \Gamma \Delta \Theta \Lambda \end{equation}` | <div class="texClass">\begin{equation} \Gamma \Delta \Theta \Lambda \end{equation}</div> | ラテン文字と同形の大文字(A, B など)はそのままの文字を使う |
| ギリシャ大文字(パイ〜オメガ) | `\begin{equation} \Pi \Sigma \Phi \Psi \Omega \end{equation}` | <div class="texClass">\begin{equation} \Pi \Sigma \Phi \Psi \Omega \end{equation}</div> |  |

## 演算子・関係記号

| 説明 | 書き方 | 数式 | 備考 |
| --- | --- | --- | --- |
| プラスマイナス | `\begin{equation} a \pm b \end{equation}` | <div class="texClass">\begin{equation} a \pm b \end{equation}</div> |  |
| 乗算 | `\begin{equation} a \times b \end{equation}` | <div class="texClass">\begin{equation} a \times b \end{equation}</div> |  |
| 中点(ドット積・乗算) | `\begin{equation} a \cdot b \end{equation}` | <div class="texClass">\begin{equation} a \cdot b \end{equation}</div> |  |
| 除算 | `\begin{equation} a \div b \end{equation}` | <div class="texClass">\begin{equation} a \div b \end{equation}</div> |  |
| 以下 | `\begin{equation} a \leq b \end{equation}` | <div class="texClass">\begin{equation} a \leq b \end{equation}</div> |  |
| 以上 | `\begin{equation} a \geq b \end{equation}` | <div class="texClass">\begin{equation} a \geq b \end{equation}</div> |  |
| 等しくない | `\begin{equation} a \neq b \end{equation}` | <div class="texClass">\begin{equation} a \neq b \end{equation}</div> |  |
| ほぼ等しい | `\begin{equation} a \approx b \end{equation}` | <div class="texClass">\begin{equation} a \approx b \end{equation}</div> |  |
| 合同・恒等 | `\begin{equation} a \equiv b \end{equation}` | <div class="texClass">\begin{equation} a \equiv b \end{equation}</div> |  |
| 比例 | `\begin{equation} a \propto b \end{equation}` | <div class="texClass">\begin{equation} a \propto b \end{equation}</div> |  |
| 十分小さい | `\begin{equation} a \ll b \end{equation}` | <div class="texClass">\begin{equation} a \ll b \end{equation}</div> |  |
| 十分大きい | `\begin{equation} a \gg b \end{equation}` | <div class="texClass">\begin{equation} a \gg b \end{equation}</div> |  |
| 属する(要素) | `\begin{equation} x \in A \end{equation}` | <div class="texClass">\begin{equation} x \in A \end{equation}</div> |  |
| 部分集合 | `\begin{equation} A \subset B \end{equation}` | <div class="texClass">\begin{equation} A \subset B \end{equation}</div> |  |
| 和集合 | `\begin{equation} A \cup B \end{equation}` | <div class="texClass">\begin{equation} A \cup B \end{equation}</div> |  |
| 共通部分 | `\begin{equation} A \cap B \end{equation}` | <div class="texClass">\begin{equation} A \cap B \end{equation}</div> |  |
| 全称記号・存在記号 | `\begin{equation} \forall x \exists y \end{equation}` | <div class="texClass">\begin{equation} \forall x \exists y \end{equation}</div> | 「すべての x」「ある y が存在する」 |
| 無限大 | `\begin{equation} \infty \end{equation}` | <div class="texClass">\begin{equation} \infty \end{equation}</div> |  |

## 矢印

| 説明 | 書き方 | 数式 | 備考 |
| --- | --- | --- | --- |
| 右矢印(写像・極限) | `\begin{equation} \to \end{equation}` | <div class="texClass">\begin{equation} \to \end{equation}</div> |  |
| 右矢印 | `\begin{equation} \rightarrow \end{equation}` | <div class="texClass">\begin{equation} \rightarrow \end{equation}</div> | `\to` と同じ形 |
| 二重右矢印(ならば) | `\begin{equation} \Rightarrow \end{equation}` | <div class="texClass">\begin{equation} \Rightarrow \end{equation}</div> |  |
| 二重両矢印(同値) | `\begin{equation} \Leftrightarrow \end{equation}` | <div class="texClass">\begin{equation} \Leftrightarrow \end{equation}</div> |  |
| 写像の対応づけ | `\begin{equation} \mapsto \end{equation}` | <div class="texClass">\begin{equation} \mapsto \end{equation}</div> |  |
| 上に文字が付く右矢印 | `\begin{equation} \xrightarrow{f} \end{equation}` | <div class="texClass">\begin{equation} \xrightarrow{f} \end{equation}</div> | 矢印の長さは上の文字に合わせて伸びる。下にも付けるときは `\xrightarrow[下]{上}` |

## 装飾(バー・ハット・ベクトル等)

| 説明 | 書き方 | 数式 | 備考 |
| --- | --- | --- | --- |
| 上線(1文字用) | `\begin{equation} \bar{x} \end{equation}` | <div class="texClass">\begin{equation} \bar{x} \end{equation}</div> | 複数文字には `\overline` を使う |
| 上線(文字数に合わせて伸びる) | `\begin{equation} \overline{\mathstrut xy} \end{equation}` | <div class="texClass">\begin{equation} \overline{\mathstrut xy} \end{equation}</div> | `\mathstrut` で文字による線の高さの違いをなくす |
| 下線 | `\begin{equation} \underline{\smash[b]{xy}} \end{equation}` | <div class="texClass">\begin{equation} \underline{\smash[b]{xy}} \end{equation}</div> | `\smash[b]` で文字による線の高さの違いをなくす |
| ハット(1文字用) | `\begin{equation} \hat{x} \end{equation}` | <div class="texClass">\begin{equation} \hat{x} \end{equation}</div> |  |
| ハット(文字数に合わせて伸びる) | `\begin{equation} \widehat{xyz} \end{equation}` | <div class="texClass">\begin{equation} \widehat{xyz} \end{equation}</div> |  |
| チルダ(1文字用) | `\begin{equation} \tilde{x} \end{equation}` | <div class="texClass">\begin{equation} \tilde{x} \end{equation}</div> |  |
| チルダ(文字数に合わせて伸びる) | `\begin{equation} \widetilde{xyz} \end{equation}` | <div class="texClass">\begin{equation} \widetilde{xyz} \end{equation}</div> |  |
| ベクトル矢印(1文字用) | `\begin{equation} \vec{v} \end{equation}` | <div class="texClass">\begin{equation} \vec{v} \end{equation}</div> | 複数文字には `\overrightarrow` を使う |
| ベクトル矢印(文字数に合わせて伸びる) | `\begin{equation} \overrightarrow{AB} \end{equation}` | <div class="texClass">\begin{equation} \overrightarrow{AB} \end{equation}</div> |  |
| ドット(時間微分) | `\begin{equation} \dot{x} \end{equation}` | <div class="texClass">\begin{equation} \dot{x} \end{equation}</div> |  |
| ダブルドット(2階の時間微分) | `\begin{equation} \ddot{x} \end{equation}` | <div class="texClass">\begin{equation} \ddot{x} \end{equation}</div> |  |
| 上側に波括弧と注釈 | `\begin{equation} \overbrace{a+b+c}^{3} \end{equation}` | <div class="texClass">\begin{equation} \overbrace{a+b+c}^{3} \end{equation}</div> | 注釈は `^` で付ける |
| 下側に波括弧と注釈 | `\begin{equation} \underbrace{a+b+c}_{3} \end{equation}` | <div class="texClass">\begin{equation} \underbrace{a+b+c}_{3} \end{equation}</div> | 注釈は `_` で付ける |

### バー・ハット等のずれ補正

| 説明 | 書き方 | 数式 | 備考 |
| --- | --- | --- | --- |
| 上線の高さが文字ごとに違う | `\begin{equation} \overline{\mathstrut a}\,\overline{\mathstrut b}\,\overline{\mathstrut x} \end{equation}` | <div class="texClass">\begin{equation} \overline{\mathstrut a}\,\overline{\mathstrut b}\,\overline{\mathstrut x} \end{equation}</div> | 各 `\overline` の中に `\mathstrut` を入れてそろえる |
| 上線の高さを揃えたい | `\begin{equation} \overline{\vphantom{b}a}\,\overline{b} \end{equation}` | <div class="texClass">\begin{equation} \overline{\vphantom{b}a}\,\overline{b} \end{equation}</div> | 背の低い文字の側に `\vphantom{b}` を入れて高さを合わせる |
| `\bar` が文字の幅に合わない | `\begin{equation} \overline{AB} \end{equation}` | <div class="texClass">\begin{equation} \overline{AB} \end{equation}</div> | `\bar` は1文字用。複数文字は `\overline` にする |
| `\bar` が文字からずれる(`i` や `j`) | `\begin{equation} \overline{\imath} \end{equation}` | <div class="texClass">\begin{equation} \overline{\imath} \end{equation}</div> | 点のない `\imath`(`\jmath` も同様)と `\overline` を組み合わせる |
| `\bar` が二重のときずれる | `\begin{equation} \overline{\overline{x}} \end{equation}` | <div class="texClass">\begin{equation} \overline{\overline{x}} \end{equation}</div> | `\bar` を重ねず、`\overline` を重ねる |
| 下線の高さが文字ごとに違う | `\begin{equation} \underline{\smash[b]{a}}\,\underline{\smash[b]{y}} \end{equation}` | <div class="texClass">\begin{equation} \underline{\smash[b]{a}}\,\underline{\smash[b]{y}} \end{equation}</div> | `\smash[b]` で下側の深さを 0 にして、下線の高さをそろえる |
| ハットが大文字で上にずれる | `\begin{equation} \widehat{A} \end{equation}` | <div class="texClass">\begin{equation} \widehat{A} \end{equation}</div> | `\widehat` に替える。複数文字を覆うときも `\widehat` |
| ベクトル矢印が短い | `\begin{equation} \overrightarrow{AB} \end{equation}` | <div class="texClass">\begin{equation} \overrightarrow{AB} \end{equation}</div> | 複数文字は `\overrightarrow` にする |

## フォント

| 説明 | 書き方 | 数式 | 備考 |
| --- | --- | --- | --- |
| 立体(ローマン体) | `\begin{equation} \mathrm{d}x \end{equation}` | <div class="texClass">\begin{equation} \mathrm{d}x \end{equation}</div> | 微分の d や単位など、変数でないものに使う |
| 太字(ボールド体) | `\begin{equation} \mathbf{A} \end{equation}` | <div class="texClass">\begin{equation} \mathbf{A} \end{equation}</div> | 行列・ベクトルによく使う。ギリシャ文字は太字にならない |
| 黒板太字 | `\begin{equation} \mathbb{R} \end{equation}` | <div class="texClass">\begin{equation} \mathbb{R} \end{equation}</div> | 実数 R などの数の集合に使う。大文字のみ |
| カリグラフィ体 | `\begin{equation} \mathcal{L} \end{equation}` | <div class="texClass">\begin{equation} \mathcal{L} \end{equation}</div> | 大文字のみ |
| フラクトゥール体(ドイツ文字) | `\begin{equation} \mathfrak{g} \end{equation}` | <div class="texClass">\begin{equation} \mathfrak{g} \end{equation}</div> |  |
| 数式中の文字列 | `\begin{equation} \text{if } x > 0 \end{equation}` | <div class="texClass">\begin{equation} \text{if } x > 0 \end{equation}</div> | `{ }` の中は数式ではなく文字列として扱われ、空白も表示される |

## 関数名

| 説明 | 書き方 | 数式 | 備考 |
| --- | --- | --- | --- |
| 三角関数 | `\begin{equation} \sin \cos \tan \end{equation}` | <div class="texClass">\begin{equation} \sin \cos \tan \end{equation}</div> | 斜体にならず立体で表示される |
| 対数(底付き) | `\begin{equation} \log_{2} x \end{equation}` | <div class="texClass">\begin{equation} \log_{2} x \end{equation}</div> |  |
| 自然対数 | `\begin{equation} \ln x \end{equation}` | <div class="texClass">\begin{equation} \ln x \end{equation}</div> |  |
| 指数関数 | `\begin{equation} \exp(x) \end{equation}` | <div class="texClass">\begin{equation} \exp(x) \end{equation}</div> |  |
| 最大値 | `\begin{equation} \max_{x} f(x) \end{equation}` | <div class="texClass">\begin{equation} \max_{x} f(x) \end{equation}</div> | 独立した数式では `x` が真下に付く |
| 任意の関数名 | `\begin{equation} \operatorname{rank} A \end{equation}` | <div class="texClass">\begin{equation} \operatorname{rank} A \end{equation}</div> | 専用コマンドがない関数名を立体で表示する |
| 最小化する引数 | `\begin{equation} \arg\min_{x} f(x) \end{equation}` | <div class="texClass">\begin{equation} \arg\min_{x} f(x) \end{equation}</div> |  |

## 行列・場合分け・複数行

| 説明 | 書き方 | 数式 | 備考 |
| --- | --- | --- | --- |
| 行列(丸括弧) | `\begin{pmatrix} a & b \\ c & d \end{pmatrix}` | <div class="texClass">\begin{pmatrix} a & b \\ c & d \end{pmatrix}</div> | `&` で列を区切り、`\\` で改行する |
| 行列(角括弧) | `\begin{bmatrix} a & b \\ c & d \end{bmatrix}` | <div class="texClass">\begin{bmatrix} a & b \\ c & d \end{bmatrix}</div> |  |
| 行列式(縦線) | `\begin{vmatrix} a & b \\ c & d \end{vmatrix}` | <div class="texClass">\begin{vmatrix} a & b \\ c & d \end{vmatrix}</div> |  |
| 場合分け | `f(x)=\begin{cases} 1 & (x>0) \\ 0 & (x\leq 0) \end{cases}` | <div class="texClass">f(x)=\begin{cases} 1 & (x>0) \\ 0 & (x\leq 0) \end{cases}</div> | `&` の左に式、右に条件を書く |
| 複数行の式(等号の位置をそろえる) | `\begin{aligned} a &= b+c \\ &= d \end{aligned}` | <div class="texClass">\begin{aligned} a &= b+c \\ &= d \end{aligned}</div> | `aligned` は数式環境(`equation` など)の中で使う |

## 空白

| 説明 | 書き方 | 数式 | 備考 |
| --- | --- | --- | --- |
| 細い空白 | `\begin{equation} a\,b \end{equation}` | <div class="texClass">\begin{equation} a\,b \end{equation}</div> | 幅 3/18 em |
| 中間の空白 | `\begin{equation} a\:b \end{equation}` | <div class="texClass">\begin{equation} a\:b \end{equation}</div> | 幅 4/18 em |
| 太い空白 | `\begin{equation} a\;b \end{equation}` | <div class="texClass">\begin{equation} a\;b \end{equation}</div> | 幅 5/18 em |
| 通常の空白 | `\begin{equation} a\ b \end{equation}` | <div class="texClass">\begin{equation} a\ b \end{equation}</div> | 文章中の空白と同じ幅 |
| 大きい空白 | `\begin{equation} a\quad b \end{equation}` | <div class="texClass">\begin{equation} a\quad b \end{equation}</div> | 幅 1 em |
| さらに大きい空白 | `\begin{equation} a\qquad b \end{equation}` | <div class="texClass">\begin{equation} a\qquad b \end{equation}</div> | 幅 2 em |
| 負の空白(詰める) | `\begin{equation} a\!b \end{equation}` | <div class="texClass">\begin{equation} a\!b \end{equation}</div> | 幅 -3/18 em |

## ルート・バーのずれ補正

### 補正用コマンド

| 説明 | 書き方 | 数式 | 備考 |
| --- | --- | --- | --- |
| 幅 0・高さ／深さは `X` と同じ見えない箱 | `\vphantom{X}` |  | 根号・上線の高さを揃える |
| 高さ 0・幅は `X` と同じ見えない箱 | `\hphantom{X}` |  | 横幅を揃える |
| 幅・高さ・深さが `X` と同じ見えない箱 | `\phantom{X}` |  | 位置合わせ全般 |
| `\vphantom{(}` と同じ | `\mathstrut` |  | 根号・上線の高さを標準に揃える |
| `X` の高さ・深さを 0 として扱う | `\smash{X}` |  | 根号が大きくなりすぎるのを防ぐ |
| 上側の高さだけ 0 にする | `\smash[t]{X}` |  | 上に突き出る文字の影響を消す |
| 下側の深さだけ 0 にする | `\smash[b]{X}` |  | `y` `g` `p` などの下端の影響を消す |
| 幅 0・高さ `h` の見えない棒 | `\rule{0pt}{h}` |  | 高さを数値で直接指定する |
| 分数・和などを大きい表示にする | `\displaystyle` |  | 根号内の分数が小さくなるのを防ぐ |
