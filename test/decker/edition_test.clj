(ns decker.edition-test
  (:use midje.sweet
        decker.edition))


(facts
 "layout -> category"

 (layout->category "normal")
 => :normal

 (layout->category "split")
 => :split

 (layout->category "double_faced_token")
 => :double

 (layout->category "weird")
 => :unknown)


(facts
 "scryfall -> card"

 (scryfall->card {:set "set"
                  :collector_number "1"
                  :name "card"
                  :layout "normal"
                  :highres_image true
                  :image_uris {:png "pngurl"}
                  :type_line "type-line"
                  :oracle_text "oracle-text"})
 => #:card{:code "set"
           :collector-number "1"
           :name "card"
           :layout "normal"
           :highres? true
           :png "pngurl"
           :type-line "type-line"
           :oracle-text "oracle-text"}


 (scryfall->card {:set "set"
                  :collector_number "1"
                  :name "card"
                  :layout "split"
                  :highres_image true
                  :image_uris {:png "pngurl"}
                  :card_faces [{:type_line "type-line-1"
                                :oracle_text "oracle-text-1"}
                               {:type_line "type-line-2"
                                :oracle_text "oracle-text-2"}]})
 => #:card{:code "set"
           :collector-number "1"
           :name "card"
           :layout "split"
           :highres? true
           :png "pngurl"
           :faces [{:type-line "type-line-1"
                    :oracle-text "oracle-text-1"}
                   {:type-line "type-line-2"
                    :oracle-text "oracle-text-2"}]}


 (scryfall->card {:set "set"
                  :collector_number "1"
                  :name "card"
                  :layout "double_faced_token"
                  :highres_image true
                  :card_faces [{:image_uris {:png "pngurl-1"}
                                :type_line "type-line-1"
                                :oracle_text "oracle-text-1"}
                               {:image_uris {:png "pngurl-2"}
                                :type_line "type-line-2"
                                :oracle_text "oracle-text-2"}]})
 => #:card{:code "set"
           :collector-number "1"
           :name "card"
           :layout "double_faced_token"
           :highres? true
           :faces [{:png "pngurl-1"
                    :type-line "type-line-1"
                    :oracle-text "oracle-text-1"}
                   {:png "pngurl-2"
                    :type-line "type-line-2"
                    :oracle-text "oracle-text-2"}]}


 (scryfall->card {:set "set"
                  :collector_number "1"
                  :name "card"
                  :layout "weird"
                  :highres_image true})
 => (throws clojure.lang.ExceptionInfo))


(facts
 "noncore editions"

 (peripheral-editions {"per-1" {"1" "card-1"}
                       "per-2" {"2" "card-2"}
                       "M10" {"3" "card-3"}})
 => #{"per-1" "per-2"})
