<?php
require_once 'config.php';

// ambil ID pengguna dari URL
$id = $_GET['id'];

// ambil data pengguna dari database
$query = "SELECT * FROM pengguna WHERE id = $id";
$result = mysqli_query($conn, $query);
$row = mysqli_fetch_assoc($result);

// cek apakah pengguna ditemukan di database
if (!$row) {
    die("Pengguna tidak ditemukan");
}

// cek apakah form disubmit
if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    // ambil data dari form
    $nama = $_POST['nama'];
    $latitude = $_POST['latitude'];
    $longitude = $_POST['longitude'];

    // validasi data
    $errors = [];
    if (empty($nama)) {
        $errors[] = "Nama harus diisi";
    }
    if (!is_numeric($latitude)) {
        $errors[] = "Latitude harus berupa angka";
    }
    if (!is_numeric($longitude)) {
        $errors[] = "Longitude harus berupa angka";
    }

    // jika tidak ada error, simpan data ke database
    if (empty($errors)) {
        // buat query untuk update data pengguna
        $query = "UPDATE pengguna SET nama = '$nama', latitude = $latitude, longitude = $longitude WHERE id = $id";
        $result = mysqli_query($conn, $query);

        if ($result) {
            // data berhasil disimpan, tampilkan pesan sukses
            $success_msg = "Data pengguna berhasil diupdate";
        } else {
            // terjadi kesalahan saat menyimpan data
            $error_msg = "Terjadi kesalahan saat menyimpan data";
        }
    }
}

?>

<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>User</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-rbsA2VBKQhggwzxH7pPCaAqO46MgnOM80zW1RWuH61DGLwZJEdK2Kadq2F9CUG65" crossorigin="anonymous">
</head>

<body>
    <div class="container">
        <?php
        include 'navbar.php'
        ?>
    </div>

    <div class="container  mt-4">
        <div class="row">
            <div class="col col-md-6">
                <?php if (!empty($errors)) : ?>
                    <div class="alert alert-danger" role="alert">
                        <?php foreach ($errors as $error) : ?>
                            <div><?php echo $error ?></div>
                        <?php endforeach; ?>
                    </div>
                <?php endif; ?>

                <?php if (isset($success_msg)) : ?>
                    <div class="alert alert-success" role="alert">
                        <?php echo $success_msg ?>
                    </div>
                <?php endif; ?>

                <?php if (isset($error_msg)) : ?>
                    <div class="alert alert-danger" role="alert">
                        <?php echo $error_msg ?>
                    </div>
                <?php endif; ?>
                <div class="card">
                    <div class="card-header">Edit User</div>
                    <div class="card-body">
                        <form method="POST">
                            <div class="mb-3">
                                <label for="nama" class="form-label">Nama</label>
                                <input type="text" class="form-control" id="nama" name="nama" value="<?php echo $row['nama'] ?>">
                            </div>
                            <div class="mb-3">
                                <label for="latitude" class="form-label">Latitude</label>
                                <input type="text" class="form-control" id="latitude" name="latitude" value="<?php echo $row['latitude'] ?>">
                            </div>
                            <div class="mb-3">
                                <label for="longitude" class="form-label">Longitude</label>
                                <input type="text" class="form-control" id="longitude" name="longitude" value="<?php echo $row['longitude'] ?>">
                            </div>
                            <div class="mb-3">
                                <label for="chat_id" class="form-label">Chat ID</label>
                                <input type="text" class="form-control" id="chat_id" name="chat_id" value="<?php echo $row['chat_id'] ?>" disabled>
                            </div>
                            <button type="submit" class="btn btn-primary btn-sm">Simpan</button>
                            <a href="user.php" class="btn btn-warning btn-sm">Kembali</a>
                        </form>
                    </div>
                </div>

            </div>
        </div>
    </div>

    <?php
    include 'footer.php'
    ?>



    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-kenU1KFdBIe4zVF0s0G1M5b4hcpxyD9F7jL+jjXkk+Q2h455rYXK/7HAuoJl+0I4" crossorigin="anonymous"></script>
</body>

</html>