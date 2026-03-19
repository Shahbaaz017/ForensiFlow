rule ExampleRule {
    strings:
        $a = "hello"
    condition:
        $a
}