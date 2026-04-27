import AppKit
import Foundation
import PDFKit
import Vision

enum OCRReaderError: Error {
    case missingPath
    case unsupportedDocument
    case cannotLoadImage
    case cannotRenderPDFPage(Int)
}

func performOCR(on image: NSImage) throws -> String {
    guard let cgImage = image.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
        throw OCRReaderError.cannotLoadImage
    }

    let request = VNRecognizeTextRequest()
    request.recognitionLevel = .accurate
    request.usesLanguageCorrection = true

    let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])
    try handler.perform([request])

    let observations = request.results ?? []
    return observations.compactMap { $0.topCandidates(1).first?.string }.joined(separator: "\n")
}

func renderPageImage(_ page: PDFPage) -> NSImage? {
    let bounds = page.bounds(for: .mediaBox)
    let width = max(Int(bounds.width * 2), 1200)
    let height = max(Int(bounds.height * 2), 1600)
    return page.thumbnail(of: NSSize(width: width, height: height), for: .mediaBox)
}

func extractTextFromPDF(url: URL) throws -> String {
    guard let document = PDFDocument(url: url) else {
        throw OCRReaderError.unsupportedDocument
    }

    var pages: [String] = []
    for index in 0..<document.pageCount {
        guard let page = document.page(at: index) else {
            throw OCRReaderError.cannotRenderPDFPage(index + 1)
        }

        let pageText = page.string?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        if !pageText.isEmpty {
            pages.append(pageText)
            continue
        }

        guard let image = renderPageImage(page) else {
            throw OCRReaderError.cannotRenderPDFPage(index + 1)
        }
        let ocrText = try performOCR(on: image).trimmingCharacters(in: .whitespacesAndNewlines)
        if !ocrText.isEmpty {
            pages.append(ocrText)
        }
    }

    return pages.joined(separator: "\n\n--- PAGE BREAK ---\n\n")
}

func extractText(from url: URL) throws -> String {
    let ext = url.pathExtension.lowercased()
    if ext == "pdf" {
        return try extractTextFromPDF(url: url)
    }

    guard let image = NSImage(contentsOf: url) else {
        throw OCRReaderError.cannotLoadImage
    }
    return try performOCR(on: image)
}

do {
    guard CommandLine.arguments.count > 1 else {
        throw OCRReaderError.missingPath
    }

    let fileURL = URL(fileURLWithPath: CommandLine.arguments[1])
    let text = try extractText(from: fileURL).trimmingCharacters(in: .whitespacesAndNewlines)
    if text.isEmpty {
        throw OCRReaderError.unsupportedDocument
    }
    print(text)
} catch {
    let message = String(describing: error)
    FileHandle.standardError.write(Data(message.utf8))
    exit(1)
}
