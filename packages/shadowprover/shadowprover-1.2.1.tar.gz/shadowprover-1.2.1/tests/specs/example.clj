
;; {:name        "*cognitive-calculus-completeness-test-13*"
;;  :description "dt5"
;;  :assumptions {1 (Knows! a1 t1 (if H (and E D)))
;;                2 (Knows! a1 t1 (Knows! a2 t2 (if (or E My) R)))
;;                3 (Knows! a1 t1 (Knows! a2 t2 (Knows! a3 t2 (if Ma (not R)))))
               
;;                4 (Attention! (if H (and E D)) )
;;                5 (Attention! (if (or E My) R)) 
;;                6 (Attention! (if Ma (not R) ))

;;                }
;;  :goal        (if H (not Ma))}


{:name        "*cognitive-calculus-completeness-test-24*"
 :description "dt10"
 :assumptions {:1 (Common! now P)}
 :goal        (Knows! a now P)}
