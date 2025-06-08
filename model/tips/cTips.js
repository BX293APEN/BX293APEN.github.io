class CPPModel{
    constructor(){
        this.type ={
            "index" : ["type", "Byte", "bit", "range"],
            "record" : [
                [
                    '<pre><code class="language-c">char</code></pre>',
                    '1',
                    '8',
                    "-128 ～ 127"
                ],
                [
                    '<pre><code class="language-c">unsigned char</code></pre>',
                    '1',
                    '8',
                    "0 ～ 255"
                ],
                [
                    '<pre><code class="language-c">short</code></pre>',
                    '2',
                    '16',
                    "-32768 ～ 32767"
                ],
                [
                    '<pre><code class="language-c">unsigned short</code></pre>',
                    '2',
                    '16',
                    "0 ～ 65535"
                ],
                [
                    '<pre><code class="language-c">int</code></pre>',
                    'CPU依存<br>16[bit]型CPU : 2<br>32[bit]型CPU : 4',
                    'CPU依存<br>16[bit]型CPU : 16<br>32[bit]型CPU : 32',
                    "CPU依存<br>16[bit]型CPU : -2<sup>15</sup> ～ 2<sup>15</sup>-1<br>32[bit]型CPU : -2<sup>31</sup> ～ 2<sup>31</sup>-1"
                ],
                [
                    '<pre><code class="language-c">long</code></pre>',
                    '4',
                    '32',
                    "-2147483648 ～ 2147483647"
                ],
                [
                    '<pre><code class="language-c">unsigned long</code></pre>',
                    '4',
                    '32',
                    "0 ～ 4294967295"
                ],
                [
                    '<pre><code class="language-c">long long</code></pre>',
                    '8',
                    '64',
                    "-2<sup>63</sup> ～ 2<sup>63</sup>-1"
                ],
                [
                    '<pre><code class="language-c">foat</code></pre>',
                    '4',
                    '32',
                    "±1.175494351 * 10<sup>-38</sup> ～ ±3.402823466 * 10<sup>38</sup>"
                ],
                [
                    '<pre><code class="language-c">double</code></pre>',
                    '8',
                    '64',
                    "±2.2250738585072014 * 10<sup>-308</sup> ～ <br>±1.7976931348623158 * 10<sup>308</sup>"
                ],
                [
                    '<pre><code class="language-c">void</code></pre>',
                    '不定',
                    '不定',
                    "不定"
                ],
            ]
        }

        this.format ={
            "index" : ["指定子", "対応する型", "説明"],
            "record" : [
                [
                    '<pre><code class="language-c">%c</code></pre>',
                    '<pre><code class="language-c">char</code></pre>',
                    '<b>c</b>haracter<br>1文字を入出力する',
                ],
                [
                    '<pre><code class="language-c">%s</code></pre>',
                    '<pre><code class="language-c">char *</code></pre>',
                    '<b>s</b>tring<br>文字列を入出力する',
                ],
                [
                    '<pre><code class="language-c">%d</code></pre>',
                    '<pre><code class="language-c">int \nshort</code></pre>',
                    '<b>d</b>ecimal<br>整数を10進数として入出力する',
                ],
                [
                    '<pre><code class="language-c">%x %X</code></pre>',
                    '<pre><code class="language-c">int\nshort\nunsigned int\nunsigned short</code></pre>',
                    'he<b>x</b>adecimal<br>整数を16進数として入出力する',
                ],
                [
                    '<pre><code class="language-c">%o %O</code></pre>',
                    '<pre><code class="language-c">int\nshort\nunsigned int\nunsigned short</code></pre>',
                    '<b>o</b>ctal<br>整数を8進数として入出力する',
                ],
                [
                    '<pre><code class="language-c">%f</code></pre>',
                    '<pre><code class="language-c">float</code></pre>',
                    '<b>f</b>loating-point number<br>実数を入出力する',
                ],
                [
                    '<pre><code class="language-c">%e</code></pre>',
                    '<pre><code class="language-c">float</code></pre>',
                    '<b>e</b>xponent<br>実数を指数表示で出力する',
                ],
                [
                    '<pre><code class="language-c">%lf</code></pre>',
                    '<pre><code class="language-c">double</code></pre>',
                    '<b>l</b>ong <b>f</b>loating-point number<br>倍精度実数を入出力する',
                ],
                [
                    '<pre><code class="language-c">%p</code></pre>',
                    '<pre><code class="language-c">void *</code></pre>',
                    '<b>p</b>ointer<br>ポインタのアドレスを入出力する'
                ],
                [
                    '<pre><code class="language-c">%%</code></pre>',
                    '-',
                    '<code>%</code>を表示'
                ],
            ]

        }

        this.escape ={
            "index" : ["エスケープシーケンス", "説明"],
            "record" : [
                [
                    '<pre><code class="language-c">\\a</code></pre>',
                    '警告音',
                ],
                [
                    '<pre><code class="language-c">\\b</code></pre>',
                    '1文字左にカーソルを移動',
                ],
                [
                    '<pre><code class="language-c">\\f</code></pre>',
                    'ページ送り (クリア)',
                ],
                [
                    '<pre><code class="language-c">\\n</code></pre>',
                    '改行',
                ],
                [
                    '<pre><code class="language-c">\\r</code></pre>',
                    '同じ行の先頭にカーソルを移動',
                ],
                [
                    '<pre><code class="language-c">\\t</code></pre>',
                    '水平タブ',
                ],
                [
                    '<pre><code class="language-c">\\v</code></pre>',
                    '垂直タブ',
                ],
                [
                    '<pre><code class="language-c">\\\\</code></pre>',
                    '<code>\\</code>を表示',
                ],
                [
                    '<pre><code class="language-c">\\?</code></pre>',
                    '<code>?</code>を表示',
                ],
                [
                    '<pre><code class="language-c">\\\'</code></pre>',
                    "<code>'</code>を表示",
                ],
                [
                    '<pre><code class="language-c">\\"</code></pre>',
                    '<code>"</code>を表示',
                ],
                [
                    '<pre><code class="language-c">\\0</code></pre>',
                    'NULL文字 (終端記号)',
                ],
                [
                    '<pre><code class="language-c">\\N</code></pre>',
                    '<code>N</code>(8進数)を表示',
                ],
                [
                    '<pre><code class="language-c">\\xN</code></pre>',
                    '<code>N</code>(16進数)を表示',
                ],
            ]
        }

        this.page =[
            {
                "page" : 1,
                "href" : "/html/tips/c.html"
            },
            {
                "page" : 2,
                "href" : "/html/tips/c2.html"
            }
        ]
    }
}

let cppModel = new CPPModel();