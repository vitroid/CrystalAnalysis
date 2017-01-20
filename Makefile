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
#軸方向に鏡映したテンプレートを作る．
%.Ax.ar3a: %.ar3a
	python $(BIN)/maketemplate2.py 8.0 10001 m 1 0 0 < $< > $@
%.Ay.ar3a: %.ar3a
	python $(BIN)/maketemplate2.py 8.0 10001 m 0 1 0 < $< > $@
%.Az.ar3a: %.ar3a
	python $(BIN)/maketemplate2.py 8.0 10001 m 0 0 1 < $< > $@
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
%.Ax.match: %.Ax.ar3a %.ar3a
	$(BIN)/slide-and-match 10000 $^ > $@
%.Ax.match2: %.Ax.ar3a %.ar3a
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
%.match.thres50.yap: %.match
	awk 'BEGIN{print "@ 3"}($$4<50){r=30./$$4;if(r>3)r=3;print "r",r;print "c",-$$1,-$$2,-$$3}' $<  > $@
%.match2.thres30.yap: %.match2
	awk 'BEGIN{print "@ 3"}($$5<30){r=30./$$5;if(r>3)r=3;print "r",r;print "c",$$2,$$3,$$4}' $<  > $@
