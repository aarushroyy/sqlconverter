const express = require('express');
const router = express.Router();
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { exec } = require('child_process'); // Import exec from child_process

// Create uploads folder if it doesn't exist
const uploadsDir = path.join(__dirname, '../uploads');
if (!fs.existsSync(uploadsDir)) {
    fs.mkdirSync(uploadsDir, { recursive: true });
}

// Create diagrams folder if it doesn't exist
const diagramsDir = path.join(__dirname, '../public/diagrams');
if (!fs.existsSync(diagramsDir)) {
    fs.mkdirSync(diagramsDir, { recursive: true });
}

// Set up storage for uploaded files
const storage = multer.diskStorage({
    destination: function (req, file, cb) {
        cb(null, uploadsDir);
    },
    filename: function (req, file, cb) {
        const originalName = file.originalname.replace('.sql', '');
        const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
        cb(null, `${originalName}-${uniqueSuffix}.sql`);
    }
});

// File filter for SQL files
const sqlFilter = function (req, file, cb) {
    if (!file.originalname.toLowerCase().endsWith('.sql')) {
        return cb(new Error('Only .sql files are allowed!'), false);
    }

    const allowedMimeTypes = ['application/sql', 'text/plain', 'application/octet-stream'];
    if (!allowedMimeTypes.includes(file.mimetype)) {
        return cb(new Error('Invalid file type. Only SQL files are allowed!'), false);
    }

    cb(null, true);
};

const upload = multer({
    storage: storage,
    fileFilter: sqlFilter,
    limits: { fileSize: 10 * 1024 * 1024 } // Limit file size to 10MB
});

function isSqlContent(filePath) {
    return new Promise((resolve, reject) => {
        fs.readFile(filePath, 'utf8', (err, data) => {
            if (err) reject(err);
            const firstLines = data.split('\n').slice(0, 10).join('\n').toLowerCase();
            const sqlKeywords = ['create', 'table', 'insert', 'select', 'drop', 'alter'];
            resolve(sqlKeywords.some(keyword => firstLines.includes(keyword)));
        });
    });
}

// File upload route
router.post('/', function (req, res) {
    upload.single('sqlFile')(req, res, async function (err) {
        if (err) {
            return res.status(400).json({ success: false, message: err.message });
        }

        if (!req.file) {
            return res.status(400).json({ success: false, message: 'No file uploaded.' });
        }

        try {
            const isSql = await isSqlContent(req.file.path);
            if (!isSql) {
                fs.unlinkSync(req.file.path);
                return res.status(400).json({ success: false, message: 'The file does not appear to contain SQL content.' });
            }

            // Generate ER diagram
            const scriptPath = path.join(__dirname, '../scripts/generate_er_diagram.py');
            const originalName = path.parse(req.file.originalname).name; // Get the name without extension
            const outputPathDot = path.join(diagramsDir, `${originalName}.dot`);
            const outputPathPng = path.join(diagramsDir, `${originalName}.png`);

            exec(`python "${scriptPath}" "${req.file.path}" "${outputPathDot}" "${outputPathPng}"`, (error, stdout, stderr) => {
                if (error) {
                    console.error(`exec error: ${error}`);
                    return res.status(500).json({ success: false, message: 'Error generating ER diagram.' });
                }
                res.status(200).json({
                    success: true,
                    message: 'File uploaded and ER diagram generated successfully',
                    file: {
                        name: req.file.originalname,
                        size: req.file.size,
                        path: req.file.path
                    },
                    diagram: `/diagrams/${originalName}.png`
                });
            });
        } catch (error) {
            res.status(500).json({ success: false, message: 'Error processing file: ' + error.message });
        }
    });
});

module.exports = router;
