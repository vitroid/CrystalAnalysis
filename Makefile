BIN=bin
all:
	cd src && make all

%.analysis1:
	make -k -j 8 $*.nx4a $*.ar3a $*.yap $*.pack38.ngph \
	$*.pack38.tetra.frag $*.pack38.tetra.ar3a \
	$*.pack38.tetra.adj.ngph $*.pack38.tetra.adj.rngs \
	$*.pack38.tetra.adj.rngs.yap $*.pack38.coord.hist


#途中の5 nmスライスだけを切り出す。ここだけはCで書いたほうがよさそう。
%.nx4a: %.gro
	$(BIN)/gro2nx4a.py < $< > $@
#Visualize the HB
%.yap: %.nx4a
	cat $(BIN)/TIP4P.id08 $(BIN)/DEFR $< | $(BIN)/trajConverter.py -y 2.5 > $@
#OH距離を基準に水素結合ネットワークを定める。
%.ngph: %.nx4a
	cat $(BIN)/TIP4P.id08 $(BIN)/DEFR $< | $(BIN)/trajConverter.py -n 2.5 > $@



#ここから先は重心のみを利用
#ラベルを付け替えて、四元数を無視する
%.ar3a: %.nx4a
	sed -e 's/NX4A/AR3A/' $< | awk '(NF==7){print $$1,$$2,$$3}(NF!=7){print}' > $@
#酸素間距離をもとに隣接関係をグラフ化する。3.8Å
%.pack38.ngph: %.ar3a
	python $(BIN)/packing-ngph.py 3.8 < $< > $@
#四面体を探す。cookfragment.plは重複を排除する。(pythonに組みこむべき)
%.tetra.frag: %.ngph
	python $(BIN)/tetrahedra.py < $< | $(BIN)/cookfragment.pl > $@
#四面体の重心位置を出力する。可視化に必要。
%.pack38.tetra.ar3a: %.ar3a %.pack38.tetra.frag
	$(BIN)/fragmentcom.pl $*.ar3a < $*.pack38.tetra.frag | sed -e 's/^@FCOM/@AR3A/' > $@
#四面体の隣接関係を調べる。これはトポロジーのみで判定可能(座標情報は要らない)。
%.tetra.adj.ngph: %.tetra.frag #$(BIN)/fragadjacency.py
	python $(BIN)/fragadjacency.py < $< > $@
#四面体の隣接関係の作る多角形(リング)を探索する。
%.rngs: %.ngph
	$(BIN)/countrings3.py 8 < $< | grep -v '^3 ' > $@
#四面体の隣接関係の作る多角形を可視化する。
%.adj.rngs.yap: %.ar3a %.adj.rngs
	cat $^ | python $(BIN)/ar3a+rngs2yap.py > $@
#配位数の分布。
%.coord.hist:%.ngph
#先頭の2行を飛ばし、最後の負の数字(terminator)も飛ばし、
#結合元と結合先を別の行に展開し、
#数値としてソートし
#出現数を数えると、それぞれの原子の配位数が得られる
#これの配位数のカラムだけを取り出し
#数値としてソートし
#出現数を数えると、配位数のヒストグラムになる。
	tail +3 $< | grep -v '^-' |\
	 awk '{print$$1;print $$2}' |\
	 sort -n |\
	 uniq -c |\
	 awk '{print $$1}' |\
	 sort -n |\
	 uniq -c > $@


#テンプレートマッチングによる、単位胞の推定
#一応定型的な手順を%.analysis2に示すが、どの分子を基準に、
#どこまでマッチングするか(並進だけか、回転や鏡映を含めるか)は、
#試行錯誤で決めざるをえない。(完全に自動化できる手順が発見できればそうするが)
%.analysis2:
	for x in A B C D E F; do echo $*.$$x.ar3a; done | xargs make -j 8 -k
	for x in A B C D E F; do echo $*.$$x.match2; done | xargs make -j 8 -k
	for x in A B C D E F; do echo $*.$$x.match2.thres30.yap; done | xargs make -j 8 -k
	for x in A B C D E F; do echo $*.$$x.match2.thres50.yap; done | xargs make -j 8 -k



#とりあえず基準はどこでもいいので、中心付近にある14配位の分子を1つ選ぶ。
#10001番分子(てきとう)
#その座標は101.032222222 2.30388888889 120.262222222
#半径8Å以内の分子だけを抽出する。(60分子程度を含む)
%.A.ar3a: %.ar3a
#	python $(BIN)/maketemplate.py 8.0 -101.032222222 -2.30388888889 -120.262222222 < $< > $@
	python $(BIN)/maketemplate2.py 8.0 10001  < $< > $@
#B： 10004番目の分子、12配位
%.B.ar3a: %.ar3a
	python $(BIN)/maketemplate2.py 8.0 10004  < $< > $@
#C： 10017番目の分子、12配位
%.C.ar3a: %.ar3a
	python $(BIN)/maketemplate2.py 8.0 10017  < $< > $@
#D： 10026番目の分子、12配位
%.D.ar3a: %.ar3a
	python $(BIN)/maketemplate2.py 8.0 10026  < $< > $@
#E： 10005番目の分子、14配位
%.E.ar3a: %.ar3a
	python $(BIN)/maketemplate2.py 8.0 10005  < $< > $@
#F： 10007番目の分子、14配位
%.F.ar3a: %.ar3a
	python $(BIN)/maketemplate2.py 8.0 10007  < $< > $@
#template Aを使って、すべての分子に対してマッチングを行う。
#出力内容は、分子番号、位置、マッチングスコア(変位の二乗和)
#スコアが一番良いのはA。
%.A.match2: %.A.ar3a %.ar3a
	$(BIN)/slide-and-match2 $^ > $@
%.B.match2: %.B.ar3a %.ar3a
	$(BIN)/slide-and-match2 $^ > $@
%.C.match2: %.C.ar3a %.ar3a
	$(BIN)/slide-and-match2 $^ > $@
%.D.match2: %.D.ar3a %.ar3a
	$(BIN)/slide-and-match2 $^ > $@
%.E.match2: %.E.ar3a %.ar3a
	$(BIN)/slide-and-match2 $^ > $@
%.F.match2: %.F.ar3a %.ar3a
	$(BIN)/slide-and-match2 $^ > $@
#良くmatchした分子の位置に○を表示
%.match2.thres50.yap: %.match2
	awk 'BEGIN{print "@ 3"}($$5<50){r=30./$$5;if(r>3)r=3;print "r",r;print "c",$$2,$$3,$$4}' $<  > $@
%.match2.thres30.yap: %.match2
	awk 'BEGIN{print "@ 3"}($$5<30){r=30./$$5;if(r>3)r=3;print "r",r;print "c",$$2,$$3,$$4}' $<  > $@
%.match2.visualize:
	make $*.A.match2.thres50.yap $*.B.match2.thres50.yap $*.C.match2.thres50.yap $*.D.match2.thres50.yap $*.E.match2.thres50.yap $*.F.match2.thres50.yap

#単位胞は、上のyaplotの出力から手作業で推定する。
#推定した単位胞の基本ベクトルは、
#a=(9.39,-9.39,0)
#b=(9.39,+9.39,0)
#c=(0, 0, 7.38)
#これを使って、平均的な分子配置を得る。
#match2ファイルのなかで、特にerrorが小さい配置だけを選び、マッチした分子配置を
#原点をずらしてすべて重ねあわせる。
#Yaplotでまず重ねた図を確認
#重なりが多すぎてまったく読めない。
%.unit.yap: %.ar3a %.ngph %.A.match2
	cat $*.ar3a $*.ngph | $(BIN)/slide-and-overlay2.py $*.A.match2 9.39 -9.39 0 9.39 9.39 0 0 0 7.38 > $@
#原点をずらしたあとの、セル内の相対座標を出力。
#これを見ると、単位胞の中の分子数は70〜80ぐらいの幅があるようだ。
#しかし、平均的な分布をみれば、どこが欠陥かはわかるはず。
%.unit.ar3r: %.ar3a %.ngph %.A.match2
	cat $*.ar3a $*.ngph | $(BIN)/slide-and-overlay2.py -A $*.A.match2 9.39 -9.39 0 9.39 9.39 0 0 0 7.38 > $@
#原子の散布図を、グリッド上の濃度分布に変換
#ずらし量を指定しているが、この量はあとのclustersの結果をもとに
#原点が最も対称性が高くなるように決めた．
%.unit.avg.grid: %.unit.ar3r Makefile #untitled: #generate an average molecular positions from unit.ar3r.  Manual work.
#	$(BIN)/ar3r2grid.py 24 0.853 0.853 0.99 < $< > $@
	$(BIN)/ar3r2grid.py 24 0.686 0.686 0.907 < $< > $@
#	$(BIN)/ar3r2grid.py 24 0.936 0.936 0.99 < $< > $@
#空間分布を等高面で可視化する。
#セル内相対座標なので、画面上では立方体として表示されているが、実際は縦にもっとつぶれている。
#それと、どうも10001番は単位胞の角の分子ではなかったらしいことがわかる。
#ずらす必要があるようだ。
%.unit.avg.grid.yap: %.unit.avg.grid
	$(BIN)/grid2yap.py 10 < $< > $@
#グリッド上で連結なクラスターに分類し、上の等高面図にいくつの塊があるかを調べる。
#クラスターのx,y,z座標、クラスターに含まれる積算分子数、クラスターに含まれるグリッドの個数。
#クラスターは72個見付かる。単位格子は72分子と思って良いのだろうか。
%.unit.avg.grid.clusters: %.unit.avg.grid
	$(BIN)/grid-cluster.py < $< > $@
#.....よくわからない。やはり、先に回転対称性をつめておく必要があるのだな。
#単位胞の角に必ず原子が存在するとは限らない(例えば氷16のように)
#結局前回同様の作業が必要なのか?

#分析4
#ここまでは，並進対称性を主眼に調査してきたが，ここからは回転や鏡映を調べる．
#そのために，大きな結晶を全部扱うのではなく，ターゲットとする分子(たぶん10001)の周辺だけを切り出して
#しまう．単位胞の大きさだけはわかっているので，あとの処理はぐっと単純にできるはず．

#Assume the symmetry from the grid data.
%.symm.yap: %.grid
	$(BIN)/symm.py < $<  > $@

#分析5
#*.clustersを作る時に、水素結合もグループ化して、どこからどこへの水素結合が一番
#多いか統計をとりたい。つまり、slide-and-overlay2の拡張が必要ということだ。
#第1段階として、matchした領域のすべての頂点と結合を、gridの座標で表現する
%.A.match2.gridbond: %.ar3a %.ngph %.A.match2
	cat $*.ar3a $*.ngph | python3 bin/clustering.py $*.A.match2 9.39 -9.39 0 9.39 9.39 0 0 0 7.38  > $@
#上の結果を統計して表示する。
%.gridbond.yap: %.gridbond
	$(BIN)/bondclusters.py 9.39 -9.39 0 9.39 9.39 0 0 0 7.38       0.686 0.686 0.907 < $< > $@
#分析6
#分析5の結果をもとに、3Dプリンタで可視化する。
