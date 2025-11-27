import os
import tempfile
import sqlite3
from k30.k30_deployer import K30Deployer

def test_generate_zpe_dna_length():
    d = K30Deployer(db_path=os.path.join(tempfile.gettempdir(), "k30_test.db"))
    dna = d.generate_zpe_dna("test-node")
    assert isinstance(dna, str)
    assert len(dna) == 144

def test_calculate_coherence_range():
    d = K30Deployer(db_path=os.path.join(tempfile.gettempdir(), "k30_test.db"))
    dna = d.generate_zpe_dna("node-1")
    c = d.calculate_coherence(dna)
    assert 0.0 <= c <= 1.0

def test_calculate_frequency_range():
    d = K30Deployer(db_path=os.path.join(tempfile.gettempdir(), "k30_test.db"))
    f = d.calculate_frequency("node-abc")
    assert 1000.0 <= f <= 51000.0

def test_persist_and_load_roundtrip(tmp_path):
    db_file = tmp_path / "k30_roundtrip.db"
    deployer = K30Deployer(db_path=str(db_file))
    deployer.deploy_core_nodes()
    deployer.deploy_ecosystem_nodes()
    count = deployer.persist_to_database()
    assert count == len(deployer.nodes)
    # Verify DB has the nodes
    conn = sqlite3.connect(str(db_file))
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM nodes")
    (n,) = cur.fetchone()
    assert n == count
    conn.close()
