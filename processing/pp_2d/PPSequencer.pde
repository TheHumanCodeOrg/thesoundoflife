private class PPSequencerEvent {
  public int note;
  
  public PPSequencerEvent(int note) {
    this.note = note;
  }
}

private class PPSequencerSlot {
  public int _notes[];
  
  public PPSequencerSlot() {
    _notes = new int[128];
    for (int i=0; i<128; i++) {
      _notes[i] = 0;
    }
  }
  
  public void toggleNote(int idx) {
    _notes[idx] = _notes[idx] == 0 ? 127 : 0;
    if (_notes[idx] == 0)
      println("Off");
  }
  
  public void clear() {
    for (int i=0; i<128; i++) {
      _notes[i] = 0;
    }
  }
}

public class PPSequencer {
  private ArrayList<PPSequencerSlot> _events;
  
  public PPSequencer(int size) {
    _events = new ArrayList<PPSequencerSlot>();
    for (int i=0; i<size; i++) {
      _events.add(new PPSequencerSlot());
    }
  }
  
  private void processSegment(List<Integer> seg) {
    // To fill the sequencer, you need the first amino acid, the last, and the length of the array
    Iterator<Integer> i = seg.iterator();
    if (seg.size() > 4) {
      Integer first = -1;
      Integer last = -1;
      Integer len = -1;
      len = seg.size();
      while (i.hasNext()) {
        Integer next = i.next();
        if (first == -1)
          first = next;
        if (!i.hasNext())
          last = next;
      }
      
      // Get an index for the first and last amino acids
      Integer noteIdx = amino2index.get(first);
      Integer offsetIdx = amino2index.get(last);
      
      int idx = 0;
      for (PPSequencerSlot slot : _events) {
        boolean hasEvent = ((idx + offsetIdx) % _events.size()) % len == 0;
        if (hasEvent) {
          slot.toggleNote(36 + noteIdx); //<>//
        }
        idx++;
      }
    }
  }
  
  public void updateWithPolypeptide(Polypeptide pp) {
    // First, clear out all of the old events
    for (PPSequencerSlot slot : _events) {
      slot.clear();
    }
    
    SegmentIntersectionEnumeration e = pp.intersectingSubsectionEnumeration();
    while(e.hasMoreElements()) {
      List<Integer> seg = e.nextElement();
      this.processSegment(seg);
    }
  }
  
  public ArrayList<PPSequencerEvent> eventsForPulseIndex(int pidx) {
    ArrayList<PPSequencerEvent> retList = new ArrayList<PPSequencerEvent>(); //<>//
    PPSequencerSlot slot = _events.get(pidx % _events.size());
    for (int i=0; i<128; i++) {
      if (slot._notes[i] > 0)
        retList.add(new PPSequencerEvent(i));
    }
    return retList;
  }
  
  public String toString() {
    return _events.toString();
  }
}