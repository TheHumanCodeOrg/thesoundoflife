import netP5.*;
import oscP5.*;
import java.util.*;

String seratonin;
String dopamine;

ArrayList<String> proteinStrings = new ArrayList<String>();

boolean needsReset = false;
LinkedList<Polypeptide> proteinList = new LinkedList<Polypeptide>();
HashMap<Polypeptide, PPSequencer> protein2sequencer = new HashMap<Polypeptide, PPSequencer>();
Polypeptide currentProtein = null;
String currentProteinString = null;
int currentProteinIndex = 0;
float proteinScaleFactor = 25;

PPSequencer sequencer;
HashMap<Integer, String> identifiers = new HashMap<Integer, String>();
HashMap<Integer, String> classifiers = new HashMap<Integer, String>();
HashMap<Integer, Double> angles = new HashMap<Integer, Double>();
HashMap<Integer, Integer> colors = new HashMap<Integer, Integer>();
HashMap<Integer, Integer> index2amino = new HashMap<Integer, Integer>();
HashMap<Integer, Integer> amino2index = new HashMap<Integer, Integer>();

OscP5 oscP5;
NetAddress myRemoteLocation;

String[] parseCollLine(String line) {
  String kv[] = line.split(",");
  String vv[] = kv[1].trim().split(" ");
  String returnArray[] = new String[vv.length+1];
  returnArray[0] = kv[0];
  for (int i=0; i<vv.length; i++) {
    returnArray[i+1] = vv[i].replace(";", "");
  }
  return returnArray;
}

HashMap<String, String[]> collToHash(String[] coll) {
  HashMap<String, String[]>retMap = new HashMap<String, String[]>();
  for (int i=0; i<coll.length; i++) {
    String line[] = parseCollLine(coll[i]);
    retMap.put(line[0], Arrays.copyOfRange(line, 1, line.length));
  }
  return retMap;
}

void setup() {
  seratonin = loadStrings("seratonin_aa.txt")[0];  
  dopamine = loadStrings("dopamine_aa.txt")[0];
  proteinStrings.add(seratonin);
  proteinStrings.add(dopamine);
  int unnamed[] = {268, 1959, 2292, 2588, 2937, 8809, 9685, 9777, 9790, 9971, 9993, 10103};
  for (int i=0; i<unnamed.length; i++) {
    String name = "protein_" + unnamed[i] + ".txt";
    String prot = loadStrings(name)[0];
    proteinStrings.add(prot);
  }
  
  String names[] = loadStrings("aa_to_name.txt");
  String indexes[] = loadStrings("aa_to_i.txt");
  String classes[] = loadStrings("classifier.txt");
  String colorstxt[] = loadStrings("class_to_color.txt");
  String anglestxt[] = loadStrings("aa_to_angle.txt");
  HashMap<String, String[]>colorMap = collToHash(colorstxt);
  
  for (int i=0; i<names.length; i++) {
    String kv[] = parseCollLine(names[i]);
    Integer aa = Integer.parseInt(kv[0]);
    identifiers.put(aa, kv[2]);
  }
  
  for (int i=0; i<indexes.length; i++) {
    String kvi[] = parseCollLine(indexes[i]);
    index2amino.put(Integer.parseInt(kvi[1]), Integer.parseInt(kvi[0]));
    amino2index.put(Integer.parseInt(kvi[0]), Integer.parseInt(kvi[1]));
  }
    
  for (int i=0; i<classes.length; i++) {
    String kvc[] = parseCollLine(classes[i]);
    Integer aa = index2amino.get(Integer.parseInt(kvc[0]));
    String colorString[] = colorMap.get(kvc[1]);
    color c = color(Integer.parseInt(colorString[0]),
                    Integer.parseInt(colorString[1]),
                    Integer.parseInt(colorString[2]));
    classifiers.put(aa, kvc[1]);
    colors.put(aa, c);
  }
  
  for (int i=0; i<anglestxt.length; i++) {
    String kva[] = parseCollLine(anglestxt[i]);
    angles.put(Integer.parseInt(kva[0]), Double.parseDouble(kva[1]));
  }
  
  oscP5 = new OscP5(this, 2323);
  oscP5.plug(this, "addAmino", "/addAmino");
  //oscP5.plug(this, "addAllAminos", "/addAllAminos");
  oscP5.plug(this, "step", "/step");
  oscP5.plug(this, "reset", "/reset");
  //oscP5.plug(this, "setProtein", "/setProtein");
  myRemoteLocation = new NetAddress("127.0.0.1", 2324);
  
  size(1000, 500);
}

void draw() {
  // Basic idea; each amino acid has a color and angle associated with it. So draw a little bend in that color, and stick them all together
  background(255);
  strokeWeight(0.25);
  
  if (needsReset)
    doReset();
    
  int proteinCount = proteinList.size();
  if (proteinCount > 0) {
    proteinCount = 4;
    float wdth = width / proteinCount;
    float hght = height;
    
      int idx = 0;
      
      synchronized(proteinList) {
        for (Polypeptide p : proteinList) {
          int row = 0;
          int col = idx;
          
          pushMatrix();
          translate((col+0.5) * wdth, (row+0.5) * hght);
          scale(proteinScaleFactor / proteinCount, proteinScaleFactor / proteinCount);
          p.drawPeptide();
          popMatrix();
          idx++;
        }
      }
  }
}

void addAmino(int aa) {
 
  // If we've already got a protein, then append this protein to the active one
  if (currentProtein != null) {
    if (aa == 0) {
      println("Finished protein, length: " + currentProtein.getPeptides().size());
      if (currentProtein.getPeptides().size() < 90) {
        synchronized(proteinList) {
          proteinList.remove(currentProtein);
        }
      }
      currentProtein = null;
    } else {
      currentProtein.appendPeptide(aa);
      sequencer.updateWithPolypeptide(currentProtein);
    }
  }
  
  // Otherwise, if the amino acid is a start codon, then start synthesizing a new protein
  else if (aa != 0 && identifiers.get(aa).equals("Met")) {
    println("Starting new protein");
    currentProtein = new Polypeptide(identifiers, angles, colors);
    currentProtein.appendPeptide(aa);
    synchronized(proteinList) {
      proteinList.addLast(currentProtein);
      if (proteinList.size() > 4) {
        proteinList.removeFirst();
      }
    }
    sequencer = new PPSequencer(32);
    protein2sequencer.put(currentProtein, sequencer);
  }
}

void addAllAminos() {
  if (currentProteinString != null) {
    for (; currentProteinIndex < currentProteinString.length(); currentProteinIndex++) {
      Integer aa = (int) currentProteinString.charAt(currentProteinIndex);
      currentProtein.appendPeptide(aa);
    }
    sequencer.updateWithPolypeptide(currentProtein);
  }
}

void reset() {
  needsReset = true;
}

void doReset() {
  proteinList.clear();
  protein2sequencer.clear();
  currentProtein = null;
  needsReset = false;
}

void setProtein(int idx) {
  if (idx < proteinStrings.size()) {
    if (currentProteinString != proteinStrings.get(idx)) {
      currentProteinString = proteinStrings.get(idx);
      reset();
    }
  }
}

void step(int step) {
  OscMessage eventMessage = new OscMessage("/events");
  for (Polypeptide p: proteinList) {
    PPSequencer s = protein2sequencer.get(p);
    ArrayList<PPSequencerEvent> events = s.eventsForPulseIndex(step);
    for (PPSequencerEvent event : events) {
      eventMessage.add(event.note);
    }
  }
  
  oscP5.send(eventMessage, myRemoteLocation);
}