import gurobi.*;

public class TestGurobi {
    public static void main(String[] args) {
        try {
            GRBEnv env = new GRBEnv(true);
            env.set("logFile", "gurobi.log");
            env.start();
            GRBModel model = new GRBModel(env);
            GRBVar x = model.addVar(0.0, 1.0, 1.0, GRB.BINARY, "x");
            model.set(GRB.IntAttr.ModelSense, GRB.MINIMIZE);
            model.optimize();
            System.out.println("Valor de x: " + x.get(GRB.DoubleAttr.X));
            model.dispose();
            env.dispose();
        } catch (GRBException e) {
            System.out.println("Erro Gurobi: " + e.getMessage());
        }
    }
}
