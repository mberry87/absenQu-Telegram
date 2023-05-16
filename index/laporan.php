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

        // Query untuk menghitung jumlah absen pagi, absen sore, sakit, izin, tidak absen pagi, dan tidak absen sore
        $sql_jumlah_absen = "SELECT 
                                SUM(CASE WHEN jenis_absen = 'absen pagi' THEN 1 ELSE 0 END) AS jumlah_absen_pagi,
                                SUM(CASE WHEN jenis_absen = 'absen sore' THEN 1 ELSE 0 END) AS jumlah_absen_sore,
                                SUM(CASE WHEN jenis_absen = 'sakit' THEN 1 ELSE 0 END) AS jumlah_sakit,
                                SUM(CASE WHEN jenis_absen = 'izin' THEN 1                             ELSE 0 END) AS jumlah_izin,
                            SUM(CASE WHEN jenis_absen != 'absen pagi' THEN 1 ELSE 0 END) AS jumlah_tidak_absen_pagi,
                            SUM(CASE WHEN jenis_absen != 'absen sore' THEN 1 ELSE 0 END) AS jumlah_tidak_absen_sore
                        FROM absen $where";

        // Menjalankan query jumlah absen
        $result_jumlah_absen = mysqli_query($conn, $sql_jumlah_absen);

        // Mengecek apakah query jumlah absen berhasil
        if ($result_jumlah_absen) {
            $row_jumlah_absen = mysqli_fetch_assoc($result_jumlah_absen);
            $jumlah_absen_pagi = $row_jumlah_absen['jumlah_absen_pagi'];
            $jumlah_absen_sore = $row_jumlah_absen['jumlah_absen_sore'];
            $jumlah_sakit = $row_jumlah_absen['jumlah_sakit'];
            $jumlah_izin = $row_jumlah_absen['jumlah_izin'];
            $jumlah_tidak_absen_pagi = $row_jumlah_absen['jumlah_tidak_absen_pagi'];
            $jumlah_tidak_absen_sore = $row_jumlah_absen['jumlah_tidak_absen_sore'];

            // Menampilkan informasi jumlah absen
            echo "Jumlah Kehadiran: " . "<br>";
            echo "Absen Pagi: " . $jumlah_absen_pagi . "<br>";
            echo "Absen Sore: " . $jumlah_absen_sore . "<br>";
            echo "Sakit: " . $jumlah_sakit . "<br>";
            echo "Izin: " . $jumlah_izin . "<br>";
            echo "Tidak Absen Pagi: " . $jumlah_tidak_absen_pagi . "<br>";
            echo "Tidak Absen Sore: " . $jumlah_tidak_absen_sore . "<br><br>";
        } else {
            echo "Query jumlah absen gagal: " . mysqli_error($conn);
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

        mysqli_close($conn);
    }
    ?>

    <br>
    <button onclick="window.print()" class="cetak">Cetak</button>
    <button>
        <a href="home.php">Kembali</a>
    </button>
</body>

</html>