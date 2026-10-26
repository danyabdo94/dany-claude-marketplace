// Put text on the macOS clipboard.
// Rich:  osascript -l JavaScript copy.js <html-file> <plain-file>
// Plain: osascript -l JavaScript copy.js --plain <plain-file>
// Slack: osascript -l JavaScript copy.js --slack <bin-file> <plain-file>
//        (bin-file comes from slack_pickle.py)
ObjC.import('AppKit');
ObjC.import('Foundation');

function readFile(path) {
  const text = $.NSString.stringWithContentsOfFileEncodingError(path, $.NSUTF8StringEncoding, null);
  if (text.isNil()) {
    throw new Error('cannot read ' + path);
  }
  return text;
}

function copySlack(binPath, plainPath) {
  const board = $.NSPasteboard.generalPasteboard;
  const plain = readFile(plainPath);
  const blob = $.NSData.dataWithContentsOfFile(binPath);
  if (blob.isNil()) {
    throw new Error('cannot read ' + binPath);
  }
  board.clearContents;
  board.setStringForType(plain, $.NSPasteboardTypeString);
  board.setDataForType(blob, 'org.chromium.web-custom-data');
  return 'slack rich text + plain on clipboard';
}

function run(argv) {
  if (argv.length === 3 && argv[0] === '--slack') {
    return copySlack(argv[1], argv[2]);
  }
  if (argv.length !== 2) {
    throw new Error('usage: copy.js <html-file> <plain-file> | copy.js --plain <plain-file> | copy.js --slack <bin-file> <plain-file>');
  }
  const board = $.NSPasteboard.generalPasteboard;
  const plain = readFile(argv[1]);
  board.clearContents;
  if (argv[0] === '--plain') {
    board.setStringForType(plain, $.NSPasteboardTypeString);
    return 'plain on clipboard';
  }
  const html = readFile(argv[0]);
  board.setStringForType(html, $.NSPasteboardTypeHTML);
  board.setStringForType(plain, $.NSPasteboardTypeString);
  return 'html + plain on clipboard';
}
