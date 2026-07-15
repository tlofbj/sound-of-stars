import AVFoundation
import Foundation

// Usage: swift play_midi.swift <path-to-midi>
let args = CommandLine.arguments
let midiPath = args.count > 1 ? args[1] : "gaia_ra_music.mid"

let midiURL = URL(fileURLWithPath: midiPath)
guard FileManager.default.fileExists(atPath: midiURL.path) else {
    FileHandle.standardError.write("MIDI file not found: \(midiURL.path)\n".data(using: .utf8)!)
    exit(1)
}

// macOS ships a General MIDI sound bank we can use as the synthesizer voice set.
let soundBankURL = URL(fileURLWithPath:
    "/System/Library/Components/CoreAudio.component/Contents/Resources/gs_instruments.dls")

do {
    let player = try AVMIDIPlayer(contentsOf: midiURL, soundBankURL: soundBankURL)
    player.prepareToPlay()
    print("Playing \(midiURL.lastPathComponent)  (duration: \(String(format: "%.1f", player.duration))s)")

    let done = DispatchSemaphore(value: 0)
    player.play {
        done.signal()
    }
    done.wait()
    print("Done.")
} catch {
    FileHandle.standardError.write("Failed to play MIDI: \(error)\n".data(using: .utf8)!)
    exit(1)
}
