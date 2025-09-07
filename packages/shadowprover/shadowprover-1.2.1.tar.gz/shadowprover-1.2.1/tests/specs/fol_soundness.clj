;;; these should not be proven!

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

{:name        "*prop-nd-false-test-1*"
 :description "Can't prove an atom from no premises"
 :assumptions {}
 :goal        P}

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

{:name        "Case sensitivity check"
 :description "Case sensitivity check"
 :assumptions {1 (or p q)}
 :goal        P}

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

{:name        "*prop-nd-false-test-2*"
 :description ""
 :assumptions {1 (and p q)}
 :goal        r}

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

{:name        "*prop-nd-false-test-3*"
 :description ""
 :assumptions {1 (if p q)}
 :goal        p}

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

{:name        "*prop-nd-false-test-4*"
 :description ""
 :assumptions {1 (if p q)}
 :goal        q}

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

{:name        "*prop-nd-false-test-5*"
 :description ""
 :assumptions {1 (if p q)}
 :goal        (not (or p (not q)))}

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

{:name        "*prop-nd-false-test-6*"
 :description ""
 :assumptions {1 (if p q)
               2 (not (not (or p (not q))))}
 :goal        (not (or p (not q)))}

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

{:name        "*prop-nd-false-test-7*"
 :description ""
 :assumptions {}
 :goal        (and p (not p))}

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

{:name        "*prop-nd-false-test-8*"
 :description ""
 :assumptions {}
 :goal        (not (not (and p (not P))))}

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

{:name        "*prop-nd-false-test-9*"
 :description ""
 :assumptions {}
 :goal        (if p (not p))}

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

{:name        "*prop-nd-false-test-10*"
 :description "existential implies universal"
 :assumptions {}
 :goal        (if (exists (?x)  (P ?x)) (forall (?y)  (P ?y)))}

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

{:name        "*prop-nd-false-test-11*"
 :description ""
 :assumptions {}
 :goal        (if (forall (?x) (exists (?y)  (Loves ?x, ?y)))
                (exists (?y) (forall (?x)  (Loves ?x, ?y))))}

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

