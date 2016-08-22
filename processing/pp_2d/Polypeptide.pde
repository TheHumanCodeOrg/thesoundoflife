public class SegmentIntersectionEnumeration implements Enumeration {
  private Polypeptide _p;
  private int _idx = 0;
  private int _prev = 0;
  
  public SegmentIntersectionEnumeration(Polypeptide p) {
    _p = p;
  }
  
  public boolean hasMoreElements() {
    if (_p.getPeptides().size() == 0)
      return false;
    if (_prev >= _p.getPeptides().size())
      return false;
    return _idx < _p.getIntersections().size()+1 ;
  }
  
  public List<Integer> nextElement() {
    Integer intersectionIdx = _idx < _p.getIntersections().size() ? _p.getIntersections().get(_idx) : _p.getPeptides().size()-1;
    _idx++;
    
    //println(intersectionIdx);
    //println("-");
    List<Integer> subsection = _p.getPeptides().subList(_prev, intersectionIdx+1);
    _prev = intersectionIdx+1;
    
    return subsection;
  }
}

public class Segment {
  public double x1, x2, y1, y2;
  
  public Segment(double x1, double y1, double x2, double y2)
  {
    this.x1 = x1;
    this.y1 = y1;
    this.x2 = x2;
    this.y2 = y2;
  }
  
  // Returns 1 if the lines intersect, otherwise 0. In addition, if the lines 
// intersect the intersection point may be stored in the floats i_x and i_y.
  public boolean intersects(Segment seg)
  {
      double s1_x, s1_y, s2_x, s2_y;
      s1_x = this.x2 - this.x1;     s1_y = this.y2 - this.y1;
      s2_x = seg.x2 - seg.x1;     s2_y = seg.y2 - seg.y1;
  
      double s, t;
      s = (-s1_y * (this.x1 - seg.x1) + s1_x * (this.y1 - seg.y1)) / (-s2_x * s1_y + s1_x * s2_y);
      t = ( s2_x * (this.y1 - seg.y1) - s2_y * (this.x1 - seg.x1)) / (-s2_x * s1_y + s1_x * s2_y);
  
      return (s >= 0 && s <= 1 && t >= 0 && t <= 1);
  }
}

public class Polypeptide {
  private HashMap<Integer, String> _identifiers;
  private HashMap<Integer, Double> _angles;
  private HashMap<Integer, Integer> _colors;
  private ArrayList<Integer> _peptides;
  private ArrayList<Integer> _intersections;
  private ArrayList<Segment> _segments;
  public int age;
  
  public Polypeptide(HashMap<Integer, String> identifiers,
                    HashMap<Integer, Double> angles,
                    HashMap<Integer, Integer> colors) 
  {
    _identifiers = identifiers;
    _angles = angles;
    _colors = colors;
    _peptides = new ArrayList<Integer>();
    _intersections = new ArrayList<Integer>();
    _segments = new ArrayList<Segment>();
    age = 0;
  }
  
  private boolean doesIntersect(Segment seg) {
    for (int i=0; i<_segments.size()-1; i++) {
      if (_segments.get(i).intersects(seg))
        return true;
    }
    return false;
  }
  
  public void appendPeptide(Integer asciiPeptideCode) 
  {
    double x=0, y=0;
    Segment lastSegment = (_segments.size() > 0) ? _segments.get(_segments.size()-1) : null;
    if (lastSegment != null) {
      x = lastSegment.x2;
      y = lastSegment.y2;
    }
    
    double angle = _angles.get(asciiPeptideCode) * TWO_PI;
    Segment newSegment = new Segment(x, y, x+cos((float)angle), y+sin((float)angle));
    if (this.doesIntersect(newSegment))
      _intersections.add(_segments.size());
    _segments.add(newSegment);
    _peptides.add(asciiPeptideCode);
  }
  
  public void reset() {
    _peptides.clear();
    _intersections.clear();
    _segments.clear();
  }
  
  public ArrayList<Integer> getPeptides() {
    return _peptides;
  }
  
  public ArrayList<Integer> getIntersections() {
    return _intersections;
  }
  
  public ArrayList<Segment> getSegments() {
    return _segments;
  }
  
  public void drawPeptide()
  {
    for (int i=0; i<_segments.size(); i++) {
      Segment seg = _segments.get(i);
      Integer aa = (int) _peptides.get(i);
      color c = _colors.get(aa);
      stroke(c);
      line((float)seg.x1, (float)seg.y1, (float)seg.x2, (float)seg.y2);
    }
  }
  
  public SegmentIntersectionEnumeration intersectingSubsectionEnumeration() {
    return new SegmentIntersectionEnumeration(this);
  }
  
  public String toString()
  {
    String retString = "";
    Integer idx = 0;
    Enumeration<Integer> e = Collections.enumeration(_peptides);
    while (e.hasMoreElements()) {
      Integer i = e.nextElement();
      String s = _identifiers.get(i);
      retString = retString.concat(s);
      if (_intersections.contains(idx))
        retString = retString.concat("\n");
      idx++;
    }
    return retString;
  }
}