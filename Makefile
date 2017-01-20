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

