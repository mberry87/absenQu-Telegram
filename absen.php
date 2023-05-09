<div class="container mt-4">
    <h1>Tabel Absen</h1>
    <table class="table">
        <thead>
            <tr>
                <th>Nama</th>
                <th>Jenis Absen</th>
                <th>Jam Absen</th>
                <th>Status</th>
                <th>Alasan</th>
            </tr>
        </thead>
        <tbody>
            <?php
            // Koneksi ke database
            require_once('config.php');

            // Query untuk mengambil data absen
            $query = "SELECT * FROM absen";

            // Eksekusi query
            $result = mysqli_query($conn, $query);

            // Looping untuk menampilkan data absen ke dalam tabel
            while ($row = mysqli_fetch_assoc($result)) {
                echo "<tr>";
                echo "<td>" . $row['nama'] . "</td>";
                echo "<td>" . $row['jenis_absen'] . "</td>";
                echo "<td>" . $row['jam_absen'] . "</td>";
                echo "<td>" . $row['status'] . "</td>";
                echo "<td>" . $row['alasan'] . "</td>";
                echo "</tr>";
            }

            // Tutup koneksi ke database
            mysqli_close($conn);
            ?>
        </tbody>
    </table>
</div>