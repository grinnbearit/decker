(defproject decker "0.1.0-SNAPSHOT"
  :description "Generates MtG decks for TTS and Proxying"
  :license {:name "EPL-2.0 OR GPL-2.0-or-later WITH Classpath-exception-2.0"
            :url "https://www.eclipse.org/legal/epl-2.0/"}
  :dependencies [[org.clojure/clojure "1.11.1"]
                 [enlive "1.1.6"]
                 [clj-http "3.12.3"]
                 [cheshire "5.10.2"]
                 [sanitize-filename "0.1.0"]]
  :repl-options {:init-ns decker.core}
  :profiles {:dev {:dependencies [[midje "1.10.5"]]}})
