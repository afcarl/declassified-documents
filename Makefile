LIBS_DIR = libs
SRC_DIR = src
DATA_DIR = data
RESULTS_DIR = results

MAX_HEAP = 1500m

JAVA_FLAGS = -server -Xmx$(MAX_HEAP) -XX:MaxPermSize=500m
#JAVA_FLAGS = -server -enableassertions -Xmx$(MAX_HEAP) -XX:MaxPermSize=500m

CP = $(LIBS_DIR)/mallet.jar:$(LIBS_DIR)/mallet-deps.jar

$(DATA_DIR)/%.dat: $(DATA_DIR)/%.csv
	java $(JAVA_FLAGS) \
	-classpath $(CP) \
	cc.mallet.classify.tui.Csv2Vectors \
	--keep-sequence \
	--line-regex "^([\\S ]*)[\\t,]*[\\S ]*[\\t,]*[\\S ]*[\\t,]*[\\S ]*[\\t,]*([\\S ]*)[\\t,]*[\\S ]*[\\t,]*[\\S ]*[\\t,]*[\\S ]*[\\t,]*(.*)$$" \
	--output $@ \
	--input $<

$(RESULTS_DIR)/lda/%/T$(T)-S$(S)-ID$(ID): $(DATA_DIR)/%.dat
	mkdir -p $@; \
	I=`expr $(S) / 10`; \
	java $(JAVA_FLAGS) \
	-classpath $(CP) \
	cc.mallet.topics.tui.Vectors2Topics \
	--input $(DATA_DIR)/$*.dat \
	--output-state $@/state.txt.gz \
	--output-topic-keys $@/topic-keys.txt.gz \
	--xml-topic-report $@/topic-report.xml \
	--xml-topic-phrase-report $@/topic-phrase-report.xml \
	--output-doc-topics $@/doc-topics.txt \
	--num-topics $(T) \
	--num-iterations $(S) \
	--output-state-interval $$I \
	--optimize-interval 5 \
	--optimize-burn-in 5 \
	> $@/stdout.txt 2>&1

# cat $(RESULTS_DIR)/lda/%/T$(T)-S$(S)-ID$(ID)/stdout.txt | awk '/LL/ { print $3 }' | python src/plot.py
