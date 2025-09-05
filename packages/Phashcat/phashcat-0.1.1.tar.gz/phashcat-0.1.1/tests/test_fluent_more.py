from Phashcat import hashcat, flags

def test_increment_and_bounds():
    cmd = (
        hashcat("h.hash", "?1?1?1?1?1?1")
        .hash_type(0).attack_mode(3)
        .cs1("?l?d")
        .increment(True).increment_min(4).increment_max(6)
        .value()
    )
    # All flags exist before positionals
    pos_i = cmd.index("h.hash")
    assert flags.INCREMENT in cmd[:pos_i]
    assert flags.INCREMENT_MIN in cmd[:pos_i]
    assert flags.INCREMENT_MAX in cmd[:pos_i]
    # Values rendered correctly
    assert cmd[cmd.index(flags.INCREMENT_MIN) + 1] == "4"
    assert cmd[cmd.index(flags.INCREMENT_MAX) + 1] == "6"

def test_charsets_1_to_8_and_outfile_json():
    b = (
        hashcat()
        .cs1("?l").cs2("?u").cs3("?d").cs4("?s")
        .cs5("?l?d").cs6("?u?s").cs7("?l?u?d").cs8("?a")
        .set(flags.OUTFILE_JSON, True)
    )
    argv = b.arg("h.hash", "?1?2?3?4?5?6?7?8").value()
    pos_i = argv.index("h.hash")
    for f in (
        flags.CUSTOM_CHARSET1, flags.CUSTOM_CHARSET2, flags.CUSTOM_CHARSET3, flags.CUSTOM_CHARSET4,
        flags.CUSTOM_CHARSET5, flags.CUSTOM_CHARSET6, flags.CUSTOM_CHARSET7, flags.CUSTOM_CHARSET8,
    ):
        assert f in argv[:pos_i]
    assert flags.OUTFILE_JSON in argv[:pos_i]

def test_brain_and_encoding_and_potfile():
    argv = (
        hashcat("h.hash", "dict.txt")
        .hash_type(0).attack_mode(0)
        .brain_client(True).brain_host("127.0.0.1").brain_port(13743).brain_password("pw")
        .encoding_from("iso-8859-15").encoding_to("utf-32le")
        .potfile_path("custom.pot").potfile_disable(True)
        .value()
    )
    pos_i = argv.index("h.hash")
    assert flags.BRAIN_CLIENT in argv[:pos_i]
    assert argv[argv.index(flags.BRAIN_HOST) + 1] == "127.0.0.1"
    assert argv[argv.index(flags.BRAIN_PORT) + 1] == "13743"
    assert argv[argv.index(flags.ENCODING_FROM) + 1] == "iso-8859-15"
    assert argv[argv.index(flags.ENCODING_TO) + 1] == "utf-32le"
    assert argv[argv.index(flags.POTFILE_PATH) + 1] == "custom.pot"
    assert flags.POTFILE_DISABLE in argv[:pos_i]
