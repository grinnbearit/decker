(ns decker.layout-test
  (:use midje.sweet
        decker.layout))


(facts
 "deck -> laylines"

 (deck->laylines {:deck/decklines
                  [{:deckline/card {:card/layout-category :normal
                                    :card/png :png-1}
                    :deckline/count 1}
                   {:deckline/card {:card/layout-category :transform
                                    :card/faces [{:png :png-2}
                                                 {:png :png-3}]}
                    :deckline/count 2}]})

 => [{:png :png-1 :count 1}
     {:png :png-2 :count 2}
     {:png :png-3 :count 2}])
