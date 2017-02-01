BIN=bin
all:
	cd src && make all

#分析1###################################################################################
%.analysis1:
	make -k -j 8 $*.nx4a $*.ar3a $*.yap $*.pack38.ngph \
	$*.pack38.tetra.frag $*.pack38.tetra.ar3a \
	$*.pack38.tetra.adj.ngph $*.pack38.tetra.adj.rngs \
	$*.pack38.tetra.adj.rngs.yap $*.pack38.coord.hist
#-------------------------------------


#1-1  途中の5 nmスライスだけを切り出す。ここだけはCで書いたほうがよさそう。
%.nx4a: %.gro
	$(BIN)/gro2nx4a.py < $< > $@
#1-2  Visualize the HB
%.yap: %.nx4a
	cat $(BIN)/TIP4P.id08 $(BIN)/DEFR $< | $(BIN)/trajConverter.py -y 2.5 > $@
#1-3  OH距離を基準に水素結合ネットワークを定める。
%.ngph: %.nx4a
	cat $(BIN)/TIP4P.id08 $(BIN)/DEFR $< | $(BIN)/trajConverter.py -n 2.5 > $@



#ここから先は重心のみを利用
#1-4  ラベルを付け替えて、四元数を無視する
%.ar3a: %.nx4a
	sed -e 's/NX4A/AR3A/' $< | awk '(NF==7){print $$1,$$2,$$3}(NF!=7){print}' > $@
#1-5  酸素間距離をもとに隣接関係をグラフ化する。3.8Å
%.pack38.ngph: %.ar3a
	python $(BIN)/packing-ngph.py 3.8 < $< > $@
#1-6  四面体を探す。cookfragment.plは重複を排除する。(pythonに組みこむべき)
%.tetra.frag: %.ngph
	python $(BIN)/tetrahedra.py < $< | $(BIN)/cookfragment.pl > $@
#1-7  四面体の重心位置を出力する。可視化に必要。
%.pack38.tetra.ar3a: %.ar3a %.pack38.tetra.frag
	$(BIN)/fragmentcom.pl $*.ar3a < $*.pack38.tetra.frag | sed -e 's/^@FCOM/@AR3A/' > $@
#1-8  四面体の隣接関係を調べる。これはトポロジーのみで判定可能(座標情報は要らない)。
%.tetra.adj.ngph: %.tetra.frag #$(BIN)/fragadjacency.py
	python $(BIN)/fragadjacency.py < $< > $@
#1-9  四面体の隣接関係の作る多角形(リング)を探索する。
%.rngs: %.ngph
	$(BIN)/countrings3.py 8 < $< | grep -v '^3 ' > $@
#1-10  四面体の隣接関係の作る多角形を可視化する。
%.adj.rngs.yap: %.ar3a %.adj.rngs
	cat $^ | python $(BIN)/ar3a+rngs2yap.py > $@
#1-11  配位数の分布。
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


#分析2###################################################################################
#テンプレートマッチングによる、単位胞の推定
#一応定型的な手順を%.analysis2に示すが、どの分子を基準に、
#どこまでマッチングするか(並進だけか、回転や鏡映を含めるか)は、
#試行錯誤で決めざるをえない。(完全に自動化できる手順が発見できればそうするが)
%.analysis2:
	for x in 1001r8 1002r8 1003r8 1004r8 1005r8 1006r8 1007r8 1008r8; do for y in ar3a match2 match2.thres30.yap match2.thres50.yap; do echo $*.$$x.$$y; done ;done | xargs make -j 8 -k
#-------------------------------------

#とりあえず基準はどこでもいいので、中心付近にある14配位の分子を1つ選ぶ。
#10001番分子(てきとう)
#その座標は101.032222222 2.30388888889 120.262222222
#2-1  半径8Å以内の分子だけを抽出する。(60分子程度を含む)
%.10001r8.ar3a: %.ar3a
	python $(BIN)/maketemplate2.py 8.0 10001  < $< > $@
%.1001r8.ar3a: %.ar3a
	python $(BIN)/maketemplate2.py 8.0 1001  < $< > $@
%.1002r8.ar3a: %.ar3a
	python $(BIN)/maketemplate2.py 8.0 1002  < $< > $@
%.1003r8.ar3a: %.ar3a
	python $(BIN)/maketemplate2.py 8.0 1003  < $< > $@
%.1004r8.ar3a: %.ar3a
	python $(BIN)/maketemplate2.py 8.0 1004  < $< > $@
%.1005r8.ar3a: %.ar3a
	python $(BIN)/maketemplate2.py 8.0 1005  < $< > $@
%.1006r8.ar3a: %.ar3a
	python $(BIN)/maketemplate2.py 8.0 1006  < $< > $@
%.1007r8.ar3a: %.ar3a
	python $(BIN)/maketemplate2.py 8.0 1007  < $< > $@
%.1008r8.ar3a: %.ar3a
	python $(BIN)/maketemplate2.py 8.0 1008  < $< > $@
#2-2  template 10001r8を使って、すべての分子に対してマッチングを行う。
#出力内容は、分子番号、位置、マッチングスコア(変位の二乗和)
%.10001r8.match2: %.10001r8.ar3a %.ar3a
	$(BIN)/slide-and-match2 $^ > $@
%.1001r8.match2: %.1001r8.ar3a %.ar3a
	$(BIN)/slide-and-match2 $^ > $@
%.1002r8.match2: %.1002r8.ar3a %.ar3a
	$(BIN)/slide-and-match2 $^ > $@
%.1003r8.match2: %.1003r8.ar3a %.ar3a
	$(BIN)/slide-and-match2 $^ > $@
%.1004r8.match2: %.1004r8.ar3a %.ar3a
	$(BIN)/slide-and-match2 $^ > $@
%.1005r8.match2: %.1005r8.ar3a %.ar3a
	$(BIN)/slide-and-match2 $^ > $@
%.1006r8.match2: %.1006r8.ar3a %.ar3a
	$(BIN)/slide-and-match2 $^ > $@
%.1007r8.match2: %.1007r8.ar3a %.ar3a
	$(BIN)/slide-and-match2 $^ > $@
%.1008r8.match2: %.1008r8.ar3a %.ar3a
	$(BIN)/slide-and-match2 $^ > $@
#2-3  良くmatchした分子の位置に○を表示
%.match2.thres50.yap: %.match2
	awk 'BEGIN{print "@ 3"}($$5<50){r=30./$$5;if(r>3)r=3;print "r",r;print "c",$$2,$$3,$$4}' $<  > $@
%.match2.thres30.yap: %.match2
	awk 'BEGIN{print "@ 3"}($$5<30){r=30./$$5;if(r>3)r=3;print "r",r;print "c",$$2,$$3,$$4}' $<  > $@
%.match2.thres20.yap: %.match2
	awk 'BEGIN{print "@ 3"}($$5<20){r=20./$$5;if(r>3)r=3;print "r",r;print "c",$$2,$$3,$$4}' $<  > $@


#分析3###################################################################################
%.analysis3:
	for x in 1005r8 ; do for y in ar3r avg.grid avg.grid.yap avg.grid.clusters ; do  echo $*.$$x.$$y; done; done | xargs make -j 8 -k
#-------------------------------------
#単位胞は、上のyaplotの出力から手作業で推定する。
#推定した単位胞の基本ベクトルは、
#a=(9.39,-9.39,0)
#b=(9.39,+9.39,0)
#c=(0, 0, 7.38)
#これを使って、平均的な分子配置を得る。
#この情報と、10001番目の分子が単位胞の中のどこにあるか(つまり、マッチした単位胞の並進)を
#%.10001r8.unitinfoに手で書きこんでおく。00010-last.10001r8.unitinfoをサンプルとして
#リポジトリに含める。
#
#3-1  match2ファイルのなかで、特にerrorが小さい配置だけを選び、マッチした分子配置を
#原点をずらしてすべて重ねあわせる。
#Yaplotでまず重ねた図を確認
#重なりが多すぎてまったく読めない。
%.10001r8.yap: %.ar3a %.ngph %.10001r8.match2 %.10001r8.unitinfo
	cat $*.ar3a $*.ngph | $(BIN)/slide-and-overlay2.py $*.10001r8.match2 $*.10001r8.unitinfo 10 > $@
#3-2  原点をずらしたあとの、セル内の相対座標を出力。
#これを見ると、単位胞の中の分子数は70〜80ぐらいの幅があるようだ。
#しかし、平均的な分布をみれば、どこが欠陥かはわかるはず。
%.10001r8.ar3r: %.ar3a %.ngph %.10001r8.match2 %.10001r8.unitinfo
	cat $*.ar3a $*.ngph | $(BIN)/slide-and-overlay2.py -A $*.10001r8.match2 $*.10001r8.unitinfo > $@
%.1005r8.ar3r: %.ar3a %.ngph %.1005r8.match2 %.1005r8.unitinfo
	cat $*.ar3a $*.ngph | $(BIN)/slide-and-overlay2.py -A $*.1005r8.match2 $*.1005r8.unitinfo > $@
#3-3  原子の散布図を、グリッド上の濃度分布に変換
#ずらし量を指定しているが、この量はあとのclustersの結果をもとに
#原点が最も対称性が高くなるように決めた．
%.avg.grid: %.ar3r %.unitinfo Makefile #untitled: #generate an average molecular positions from ar3r.
	$(BIN)/ar3r2grid.py 24 $*.unitinfo < $< > $@
#3-4  空間分布を等高面で可視化する。
#セル内相対座標なので、画面上では立方体として表示されているが、実際は縦にもっとつぶれている。
#それと、どうも10001番は単位胞の角の分子ではなかったらしいことがわかる。
#ずらす必要があるようだ。
%.avg.grid.yap: %.avg.grid
	$(BIN)/grid2yap.py 10 < $< > $@
#3-5  グリッド上で連結なクラスターに分類し、上の等高面図にいくつの塊があるかを調べる。
#クラスターのx,y,z座標、クラスターに含まれる積算分子数、クラスターに含まれるグリッドの個数。
#クラスターは72個見付かる。単位格子は72分子と思って良いのだろうか。
%.avg.grid.clusters: %.avg.grid
	$(BIN)/grid-cluster.py < $< > $@
#.....よくわからない。やはり、先に回転対称性をつめておく必要があるのだな。
#単位胞の角に必ず原子が存在するとは限らない(例えば氷16のように)
#結局前回同様の作業が必要なのか?






#分析4###################################################################################
#ここまでは，並進対称性を主眼に調査してきたが，ここからは回転や鏡映を調べる．
#そのために，大きな結晶を全部扱うのではなく，ターゲットとする分子(たぶん10001)の周辺だけを切り出して
#しまう．単位胞の大きさだけはわかっているので，あとの処理はぐっと単純にできるはず．
%.analysis4:
	for x in 1005r8 ; do for y in avg.symm.yap ; do  echo $*.$$x.$$y; done; done | xargs make -j 8 -k
#-------------------------------------
#4-1  Assume the symmetry from the grid data.
%.symm.yap: %.grid
	$(BIN)/symm.py < $<  > $@





#分析5###################################################################################
#*.clustersを作る時に、水素結合もグループ化して、どこからどこへの水素結合が一番
#多いか統計をとりたい。
%.analysis5:
	for x in 1005r8 ; do for y in gridbond gridbond.yap ; do  echo $*.$$x.$$y; done; done | xargs make -j 8 -k
#-------------------------------------
#5-1  matchした領域のすべての頂点と結合を、gridの座標で表現する
%.10001r8.gridbond: %.ar3a %.ngph %.10001r8.match2
	cat $*.ar3a $*.ngph | python3 bin/gridify.py $*.10001r8.match2 $*.10001r8.unitinfo 10 24 > $@
%.1005r8.gridbond: %.ar3a %.ngph %.1005r8.match2
	cat $*.ar3a $*.ngph | python3 bin/gridify.py $*.1005r8.match2 $*.1005r8.unitinfo 10 24 > $@
#5-2  上の結果を統計して表示する。
%.gridbond.yap: %.avg.grid %.gridbond %.unitinfo
	$(BIN)/showgridbonds.py $*.unitinfo $*.avg.grid < $*.gridbond > $@
#分析6
#分析5の結果をもとに、3Dプリンタで可視化する。
#5-2  上の結果を統計して表示する。
%.gridbond.scad: %.avg.grid %.gridbond %.unitinfo
	$(BIN)/showgridbonds.py -s $*.unitinfo $*.avg.grid < $*.gridbond > $@
