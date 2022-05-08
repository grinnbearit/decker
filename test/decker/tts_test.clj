(ns decker.tts-test
  (:use midje.sweet
        decker.tts))


(facts
 "card -> ObjectState"
 (card->ObjectState #:card{:png "png-url"
                           :layout "planar"
                           :layout-category :normal})
 => {"FaceURL" "png-url"
     "BackURL" (BACK-URL "planar")
     "NumHeight" 1
     "NumWidth" 1
     "BackIsHidden" true}


 (card->ObjectState #:card{:png "png-url"
                           :layout-category :split})
 => {"FaceURL" "png-url"
     "BackURL" (BACK-URL "normal")
     "NumHeight" 1
     "NumWidth" 1
     "BackIsHidden" true}


 (card->ObjectState #:card{:faces [{:png "png-url-1"}
                                   {:png "png-url-2"}]
                           :layout-category :transform})
 => {"FaceURL" "png-url-1"
     "BackURL" (BACK-URL "normal")
     "NumHeight" 1
     "NumWidth" 1
     "BackIsHidden" true}


 (card->ObjectState #:card{:faces [{:png "png-url-1"}
                                   {:png "png-url-2"}]
                           :layout-category :transform}
                    true)
 => {"FaceURL" "png-url-2"
     "BackURL" (BACK-URL "normal")
     "NumHeight" 1
     "NumWidth" 1
     "BackIsHidden" true})


(facts
 "card -> Description"

 (card->Description #:card{:layout-category :normal
                           :type-line "type line"
                           :oracle-text "oracle text"})
 => (str "[b]type line[/b]"
         "\n\n"
         "oracle text")


 (card->Description #:card{:layout-category :split
                           :faces [{:type-line "type line 1"
                                    :oracle-text "oracle text 1"}
                                   {:type-line "type line 2"
                                    :oracle-text "oracle text 2"}]})
 => (str "[b]type line 1[/b]"
         "\n\n"
         "oracle text 1"
         "\n\n"
         "--------------------------"
         "\n\n"
         "[b]type line 2[/b]"
         "\n\n"
         "oracle text 2")


 (card->Description #:card{:layout-category :double
                           :faces [{:type-line "type line 1"
                                    :oracle-text "oracle text 1"}
                                   {:type-line "type line 2"
                                    :oracle-text "oracle text 2"}]})
 => (str "[b]type line 1[/b]"
         "\n\n"
         "oracle text 1")


 (card->Description #:card{:layout-category :double
                           :faces [{:type-line "type line 1"
                                    :oracle-text "oracle text 1"}
                                   {:type-line "type line 2"
                                    :oracle-text "oracle text 2"}]}
                    true)
 => (str "[b]type line 2[/b]"
         "\n\n"
         "oracle text 2"))


(facts
 "card -> contained object"

 (tts-card->ContainedObject #:tts-card{:tts-id 100
                                       :card #:card{:name "card-name"
                                                    :layout-category :normal}})
 => {"Name" "Card",
     "Transform" {"posX" 0.0 "posY" 0.0 "posZ" 0.0
                  "rotX" 0.0 "rotY" 180.0 "rotZ" 180.0
                  "scaleX" 1.0 "scaleY" 1.0, "scaleZ" 1.0}
     "Nickname" "card-name"
     "Description" "card-description"
     "CardID" 100}

 (provided
  (card->Description #:card{:name "card-name"
                            :layout-category :normal}
                     false)
  => "card-description")

 (tts-card->ContainedObject #:tts-card{:faces [{:tts-id 100}
                                               {:tts-id 200}]
                                       :card #:card{:name "card-name"
                                                    :layout-category :transform}})
 => {"Name" "Card",
     "Transform" {"posX" 0.0 "posY" 0.0 "posZ" 0.0
                  "rotX" 0.0 "rotY" 180.0 "rotZ" 180.0
                  "scaleX" 1.0 "scaleY" 1.0, "scaleZ" 1.0}
     "Nickname" "card-name"
     "Description" "card-description-1"
     "CardID" 100
     "States" {"2" {"Name" "Card",
                    "Transform" {"posX" 0.0 "posY" 0.0 "posZ" 0.0
                                 "rotX" 0.0 "rotY" 180.0 "rotZ" 180.0
                                 "scaleX" 1.0 "scaleY" 1.0, "scaleZ" 1.0}
                    "Nickname" "card-name"
                    "Description" "card-description-2"
                    "CardID" 200}}}

 (provided
  (card->Description #:card{:name "card-name"
                            :layout-category :transform}
                     false)
  => "card-description-1"
  (card->Description #:card{:name "card-name"
                            :layout-category :transform}
                     true)
  => "card-description-2"))


(facts
 "deck -> tts-cards"

 (deck->tts-cards #:deck{:decklines [#:deckline{:count 2 :card #:card{:name "card-1" :layout-category :normal}}
                                     #:deckline{:count 1 :card #:card{:name "card-2" :layout-category :normal}}
                                     #:deckline{:count 1 :card #:card{:name "card-3" :layout-category :transform}}]})
 => [#:tts-card{:tts-id 100
                :card #:card{:name "card-1" :layout-category :normal}}
     #:tts-card{:tts-id 100
                :card #:card{:name "card-1" :layout-category :normal}}
     #:tts-card{:tts-id 200
                :card #:card{:name "card-2" :layout-category :normal}}
     #:tts-card{:faces [{:tts-id 300}
                        {:tts-id 400}]
                :card #:card{:name "card-3" :layout-category :transform}}])


(facts
 "tts-cards -> CustomDeck"

 (tts-cards->CustomDeck [#:tts-card{:tts-id 100
                                    :card #:card{:name "card-1" :layout-category :normal}}
                         #:tts-card{:tts-id 100
                                    :card #:card{:name "card-1" :layout-category :normal}}
                         #:tts-card{:tts-id 200
                                    :card #:card{:name "card-2" :layout-category :normal}}
                         #:tts-card{:faces [{:tts-id 300}
                                            {:tts-id 400}]
                                    :card #:card{:name "card-3" :layout-category :transform}}])
 => {"1" "object-1"
     "2" "object-2"
     "3" "object-3"
     "4" "object-4"}

 (provided
  (card->ObjectState #:card{:name "card-1" :layout-category :normal})
  => "object-1"

  (card->ObjectState #:card{:name "card-2" :layout-category :normal})
  => "object-2"

  (card->ObjectState #:card{:name "card-3" :layout-category :transform})
  => "object-3"

  (card->ObjectState #:card{:name "card-3" :layout-category :transform} true)
  => "object-4"))


(facts
 "deck -> tts-deck"

 (deck->tts-deck #:deck{:name "deck"
                        :description "description"
                        :decklines [#:deckline{:name "card-1"}
                                    #:deckline{:name "card-2"}]})
 => {"ObjectStates" [{"Name" "DeckCustom"
                      "Nickname" "deck"
                      "Description" "description"
                      "Transform" {"posX" 0.0 "posY" 1.0 "posZ" 0.0
                                   "rotX" 0.0 "rotY" 180.0 "rotZ" 180.0
                                   "scaleX" 1.0 "scaleY" 1.0 "scaleZ" 1.0}
                      "DeckIDs" [100 200]
                      "CustomDeck" "custom-deck"
                      "ContainedObjects" [{"CardID" 100}
                                          {"CardID" 200}]}]}

 (provided
  (deck->tts-cards #:deck{:name "deck"
                          :description "description"
                          :decklines [#:deckline{:name "card-1"}
                                      #:deckline{:name "card-2"}]})
  => [#:tts-card{:tts-id 100
                 :card #:card{:name "card-1"}}
      #:tts-card{:tts-id 200
                 :card #:card{:name "card-2"}}]

  (tts-cards->CustomDeck [#:tts-card{:tts-id 100
                                     :card #:card{:name "card-1"}}
                          #:tts-card{:tts-id 200
                                     :card #:card{:name "card-2"}}])
  => "custom-deck"

  (tts-card->ContainedObject #:tts-card{:tts-id 100
                                        :card #:card{:name "card-1"}})
  => {"CardID" 100}

  (tts-card->ContainedObject #:tts-card{:tts-id 200
                                        :card #:card{:name "card-2"}})
  => {"CardID" 200}))
