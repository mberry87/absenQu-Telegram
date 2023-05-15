<!DOCTYPE html>
<html>

<head>
    <title>Laporan Absensi</title>
</head>

<style>
    button a {
        text-decoration: none;
        color: #000;
    }

    @media print {

        form,
        button,
        a,
        .cetak {
            display: none;
        }
    }
</style>

<body>
    <h3>Laporan Absensi</h3>
    <form method="post" action="laporan.php">
        <label for="tgl_awal">Tanggal Awal:</label>
        <input type="date" name="tgl_awal" id="tgl_awal" required>
        <label for="tgl_akhir">Tanggal Akhir:</label>
        <input type="date" name="tgl_akhir" id="tgl_akhir" required>
        <label for="nama">Nama:</label>
        <select name="nama" id="nama">
            <option value="">-- Pilih Nama --</option>
            <?php
            require_once('config.php');
            // Query untuk mengambil daftar nama
            $sql = "SELECT DISTINCT nama FROM absen ORDER BY nama ASC";

            // Menjalankan query
            $result = mysqli_query($conn, $sql);

            // Mengecek apakah query berhasil
            if (!$result) {
                die("Query gagal: " . mysqli_error($conn));
            }

            // Menampilkan daftar nama dalam dropdown
            while ($row = mysqli_fetch_assoc($result)) {
                echo "<option value='" . $row['nama'] . "'>" . $row['nama'] . "</option>";
            }
            ?>
        </select>


        <button type="submit">Pilih</button>
    </form>
    <br>
    <?php
    // Mengambil nilai dari form jika sudah disubmit
    if ($_SERVER['REQUEST_METHOD'] === 'POST') {
        $tgl_awal = $_POST['tgl_awal'];
        $tgl_akhir = $_POST['tgl_akhir'];
        $nama = $_POST['nama'];
        $where = "WHERE (jam_absen BETWEEN '$tgl_awal' AND '$tgl_akhir') ";
        if (!empty($nama)) {
            $where .= "AND nama = '$nama' ";
        }
    } else {
        $where = "";
    }

    // Koneksi ke database
    require_once('config.php');

    // Query untuk mengambil data absensi
    $sql = "SELECT id, nama, jenis_absen, status, alasan, jam_absen FROM absen $where ORDER BY jam_absen DESC";

    // Menjalankan query
    $result = mysqli_query($conn, $sql);

    // Mengecek apakah query berhasil
    if (!$result) {
        die("Query gagal: " . mysqli_error($conn));
    }

    // Menampilkan tabel absensi
    if (mysqli_num_rows($result) > 0) {
        echo "<table border='1'>";
        echo "<thead>";
        echo "<tr>";

        echo "<th>Nama</th>";
        echo "<th>Jenis Absen</th>";
        echo "<th>Status</th>";
        echo "<th>Alasan</th>";
        echo "<th>Jam Absen</th>";
        echo "</tr>";
        echo "</thead>";
        echo "<tbody>";
        while ($row = mysqli_fetch_assoc($result)) {
            echo "<tr>";

            echo "<td>" . $row['nama'] . "</td>";
            echo "<td>" . $row['jenis_absen'] . "</td>";
            echo "<td>" . $row['status'] . "</td>";
            echo "<td>" . $row['alasan'] . "</td>";
            echo "<td>" . $row['jam_absen'] . "</td>";
            echo "</tr>";
        }
        echo "</tbody>";
        echo "</table>";
    } else {
        echo "Tidak ada data absensi.";
    }
    ?>

    <br>
    <button onclick="window.print()" class="cetak">Cetak</button>
    <button>
        <a href="home.php">Kembali</a>
    </button>
</body>

</html>